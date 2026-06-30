from sqlalchemy.orm import Session
from app.models.db_models import SeismicEventDB, FeedbackDB

def create_event(db: Session, data: dict):
    event = SeismicEventDB(**data)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

def get_event_by_id(db: Session, event_id: str):
    return db.query(SeismicEventDB).filter(SeismicEventDB.event_id == event_id).first()

def mark_dispatched(db: Session, event_id: str, message: str):
    event = get_event_by_id(db, event_id)
    if event:
        event.dispatched = True
        event.public_message = message
        db.commit()
        db.refresh(event)
    return event

def save_feedback(db: Session, event_id: str, was_correct: bool, note: str | None = None):
    feedback = FeedbackDB(event_id=event_id, was_correct=was_correct, note=note)
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback

def approve_event(db: Session, event_id: str, message: str):
    event = get_event_by_id(db, event_id)
    if event:
        event.action = "alert_sent"
        event.public_message = message
        event.dispatched = True
        db.commit()
        db.refresh(event)
    return event


def reject_event(db: Session, event_id: str, reason: str | None = None):
    event = get_event_by_id(db, event_id)
    if event:
        event.action = "rejected"
        if reason:
            event.rationale = (event.rationale or "") + f" | Rechazado por operador: {reason}"
        db.commit()
        db.refresh(event)
    return event

def list_pending_events(db: Session):
    return (
        db.query(SeismicEventDB)
        .filter(SeismicEventDB.action == "pending_human_review")
        .order_by(SeismicEventDB.id.desc())
        .all()
    )