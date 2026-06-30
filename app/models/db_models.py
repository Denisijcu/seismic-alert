from sqlalchemy import Column, String, Float, Boolean, Integer, Text
from app.core.db import Base

class SeismicEventDB(Base):
    __tablename__ = "seismic_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    depth_km = Column(Float, nullable=False)
    magnitude = Column(Float, nullable=False)
    timestamp_utc = Column(String, nullable=False)
    source = Column(String, default="unknown")
    severity = Column(String, default="low")
    confidence = Column(Float, default=0.0)
    action = Column(String, default="monitor")
    rationale = Column(Text, nullable=True)
    public_message = Column(Text, nullable=True)
    dispatched = Column(Boolean, default=False)

class FeedbackDB(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, index=True, nullable=False)
    was_correct = Column(Boolean, nullable=False)
    note = Column(Text, nullable=True)