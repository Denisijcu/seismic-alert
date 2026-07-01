import json
import re
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.utils import clean_message, extract_severity, strip_json_fences
from app.models.schemas import Feedback, SeismicEvent
from app.orchestration.router import run_pipeline
from app.agents.dispatcher import dispatch_alert
from app.repositories import (
    create_event,
    mark_dispatched,
    save_feedback,
    get_event_by_id,
    approve_event,
    reject_event,
    list_pending_events,
)

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"


def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


PROMPTS = {
    "classifier": load_prompt("classifier.txt"),
    "validator": load_prompt("validator.txt"),
    "redactor": load_prompt("redactor.txt"),
}


@router.post("/ingest/event")
def ingest_event(event: SeismicEvent, db: Session = Depends(get_db)):
    result = run_pipeline(event.model_dump(), PROMPTS)

    public_message = clean_message(result.get("message"))
    if public_message and result.get("status") == "pending_human_review":
        result["message"] = public_message

    stored = create_event(
        db,
        {
            **event.model_dump(),
            "severity":       extract_severity(result.get("classification", "")),
            "confidence":     result.get("validation", {}).get("confidence", 0.0),
            "action":         result.get("status", "monitor"),
            "rationale":      str(result),
            "public_message": public_message,
        },
    )

    return {"db_id": stored.id, "result": result}


@router.post("/events/{event_id}/approve")
def approve(event_id: str, db: Session = Depends(get_db)):
    event = get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.action != "pending_human_review":
        raise HTTPException(
            status_code=409,
            detail=f"Event is not pending review (current action: {event.action})",
        )

    dispatched = dispatch_alert(event.public_message or "", ["push", "sms", "telegram"])
    approve_event(db, event_id, event.public_message or "")

    return {"event_id": event_id, "status": "alert_sent", "dispatch": dispatched}


@router.post("/events/{event_id}/reject")
def reject(event_id: str, reason: str | None = None, db: Session = Depends(get_db)):
    event = get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.action != "pending_human_review":
        raise HTTPException(
            status_code=409,
            detail=f"Event is not pending review (current action: {event.action})",
        )

    reject_event(db, event_id, reason)
    return {"event_id": event_id, "status": "rejected"}


@router.get("/events/pending")
def get_pending_events(db: Session = Depends(get_db)):
    events = list_pending_events(db)
    return {
        "count": len(events),
        "events": [
            {
                "event_id":      e.event_id,
                "magnitude":     e.magnitude,
                "depth_km":      e.depth_km,
                "latitude":      e.latitude,
                "longitude":     e.longitude,
                "timestamp_utc": e.timestamp_utc,
                "severity":      e.severity,
                "confidence":    e.confidence,
                "public_message": e.public_message,
            }
            for e in events
        ],
    }


@router.post("/feedback")
def feedback(payload: Feedback, db: Session = Depends(get_db)):
    saved = save_feedback(db, payload.event_id, payload.was_correct, payload.note)
    return {"stored": True, "id": saved.id}