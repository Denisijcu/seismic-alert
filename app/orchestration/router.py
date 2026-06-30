import json
from app.agents.classifier import classify_event
from app.agents.validator import validate_event
from app.agents.redactor import redact_message
from app.agents.dispatcher import dispatch_alert


def _hard_safety_override(event: dict) -> bool:
    """
    Umbral de seguridad duro, independiente del LLM.
    Si un evento cumple estas condiciones, se alerta sí o sí,
    sin depender de que el modelo lo interprete bien.
    """
    mag = float(event.get("magnitude", 0))
    depth = float(event.get("depth_km", 999))

    if mag >= 6.0 and depth <= 20:
        return True
    if mag >= 7.0 and depth <= 70:
        return True
    return False


def run_pipeline(event: dict, prompts: dict):
    risk_check = __import__("app.seismic.detector", fromlist=["detect_seismic_risk"]).detect_seismic_risk(event)
    if not risk_check["valid"]:
        return {"status": "discarded", "reason": "below threshold"}

    classification_raw = classify_event(event, prompts["classifier"])
    validation_raw = validate_event({"event": event, "classification": classification_raw}, prompts["validator"])

    try:
        validation = json.loads(validation_raw)
        alert_needed = validation.get("should_alert", False)
    except Exception:
        validation = {"should_alert": False, "confidence": 0.0, "reason": "parse error"}
        alert_needed = False

    hard_override = _hard_safety_override(event)
    if hard_override:
        alert_needed = True
        validation.setdefault("reason", "hard safety threshold triggered")

    if not alert_needed:
        return {
            "status": "monitor",
            "classification": classification_raw,
            "validation": validation,
        }

    # Evento necesita alerta -> se redacta el mensaje, pero se queda
    # pendiente de aprobación humana (HITL) antes de despachar.
    message = redact_message(
        {"event": event, "classification": classification_raw, "validation": validation},
        prompts["redactor"],
    )

    return {
        "status": "pending_human_review",
        "classification": classification_raw,
        "validation": validation,
        "message": message,
        "hard_override": hard_override,
    }