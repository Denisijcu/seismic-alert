import logging
from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.core.db import SessionLocal
from app.core.redis_client import redis_client
from app.core.utils import clean_message, extract_severity
from app.orchestration.router import run_pipeline
from app.repositories import create_event

logger = logging.getLogger("usgs_poller")

REDIS_PREFIX = "usgs:processed:"
REDIS_TTL = 86400  # 24 horas — ventana razonable para deduplicar eventos USGS

PROMPTS: dict | None = None


def _load_prompts() -> dict:
    """Carga los prompts una sola vez — el worker vive en un thread separado."""
    global PROMPTS
    if PROMPTS is None:
        from pathlib import Path
        base = Path(__file__).resolve().parent.parent
        prompts_dir = base / "prompts"
        PROMPTS = {
            "classifier": (prompts_dir / "classifier.txt").read_text(encoding="utf-8"),
            "validator":  (prompts_dir / "validator.txt").read_text(encoding="utf-8"),
            "redactor":   (prompts_dir / "redactor.txt").read_text(encoding="utf-8"),
        }
    return PROMPTS


def _normalize_usgs_feature(feature: dict) -> dict | None:
    """
    Convierte un feature de GeoJSON de USGS al modelo interno SeismicEvent.
    Devuelve None si faltan campos críticos.

    USGS GeoJSON:
      feature.id                        → event_id
      feature.properties.mag            → magnitude
      feature.geometry.coordinates[0]   → longitude
      feature.geometry.coordinates[1]   → latitude
      feature.geometry.coordinates[2]   → depth_km
      feature.properties.time           → timestamp_utc (epoch ms)
    """
    try:
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [])

        if len(coords) < 3:
            return None
        if props.get("mag") is None:
            return None

        ts_ms = props.get("time", 0)
        timestamp_utc = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        return {
            "event_id":      feature["id"],
            "magnitude":     float(props["mag"]),
            "longitude":     float(coords[0]),
            "latitude":      float(coords[1]),
            "depth_km":      float(coords[2]),
            "timestamp_utc": timestamp_utc,
            "source":        "usgs",
        }
    except Exception as e:
        logger.warning(f"Error normalizando feature USGS: {e}")
        return None


def _already_processed(event_id: str) -> bool:
    """Verifica si el evento ya fue procesado usando Redis como cache."""
    return redis_client.exists(f"{REDIS_PREFIX}{event_id}") == 1


def _mark_processed(event_id: str) -> None:
    """Marca el evento como procesado en Redis con TTL de 24h."""
    redis_client.setex(f"{REDIS_PREFIX}{event_id}", REDIS_TTL, "1")


def poll_usgs() -> None:
    """
    Job principal — se ejecuta cada USGS_POLL_INTERVAL_SECONDS.
    1. Descarga el feed GeoJSON de USGS (últimas horas)
    2. Filtra eventos ya procesados (Redis)
    3. Normaliza cada feature al modelo interno
    4. Corre el pipeline de IA (detector → classify → validate → redact)
    5. Persiste resultado en Postgres
    6. Marca el evento como procesado en Redis
    """
    logger.info("USGS poller: iniciando ciclo de polling...")

    try:
        response = httpx.get(settings.usgs_feed_url, timeout=15.0)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error(f"USGS poller: error descargando feed: {e}")
        return

    features = data.get("features", [])
    logger.info(f"USGS poller: {len(features)} eventos en el feed")

    new_count = 0
    discarded_count = 0

    prompts = _load_prompts()
    db = SessionLocal()

    try:
        for feature in features:
            event_id = feature.get("id")
            if not event_id:
                continue

            if _already_processed(event_id):
                continue

            event = _normalize_usgs_feature(feature)
            if event is None:
                _mark_processed(event_id)
                continue

            try:
                result = run_pipeline(event, prompts)

                public_message = clean_message(result.get("message"))
                if public_message and result.get("status") == "pending_human_review":
                    result["message"] = public_message

                create_event(
                    db,
                    {
                        **event,
                        "severity":       extract_severity(result.get("classification", "")),
                        "confidence":     result.get("validation", {}).get("confidence", 0.0),
                        "action":         result.get("status", "monitor"),
                        "rationale":      str(result),
                        "public_message": public_message,
                    },
                )

                _mark_processed(event_id)
                new_count += 1

                status = result.get("status")
                logger.info(
                    f"USGS poller: [{event_id}] mag={event['magnitude']} "
                    f"depth={event['depth_km']}km → {status}"
                )

                if status == "discarded":
                    discarded_count += 1

            except Exception as e:
                logger.error(f"USGS poller: error procesando {event_id}: {e}")
                db.rollback()
                # No marcamos como procesado — lo reintentará en el próximo ciclo

    finally:
        db.close()

    logger.info(
        f"USGS poller: ciclo completado — "
        f"{new_count} nuevos ({new_count - discarded_count} válidos, {discarded_count} descartados)"
    )