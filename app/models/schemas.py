
from pydantic import BaseModel
from typing import Optional, Literal

class SeismicEvent(BaseModel):
    event_id: str
    latitude: float
    longitude: float
    depth_km: float
    magnitude: float
    timestamp_utc: str
    source: str = "unknown"

class ImpactDecision(BaseModel):
    severity: Literal["low", "medium", "high", "critical"]
    confidence: float
    eta_seconds: Optional[int] = None
    action: Literal["monitor", "validate", "alert"]
    rationale: str
    public_message: Optional[str] = None

class Feedback(BaseModel):
    event_id: str
    was_correct: bool
    note: Optional[str] = None