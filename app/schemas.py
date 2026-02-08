"""HIR MVP — API schemas (Pydantic models)."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# --- H-Event ---

class HEventCreate(BaseModel):
    harm_type: str  # direct | indirect | systemic | deferred
    harm_domain: str
    description: str
    severity: str  # low | medium | high | critical
    confidence: str  # low | medium | high | confirmed
    affected_scope: str = "individual"
    affected_count: Optional[int] = None
    horizon: str = "immediate"
    source_type: str  # automated | human | audit | external
    source_id: Optional[str] = None
    metadata: Optional[dict] = None


class HEventStatusUpdate(BaseModel):
    status: str
    reason: str


class HEventResponse(BaseModel):
    h_id: str
    status: str
    harm_type: str
    harm_domain: str
    description: str
    severity: str
    confidence: str
    affected_scope: str
    affected_count: Optional[int]
    horizon: str
    source_type: str
    source_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- H-Stop ---

class HStopCreate(BaseModel):
    h_id: str
    measure: str  # pause | rate_limit | scope_reduction | manual_mode
    scope_target: Optional[str] = None
    reason: str
    initiated_by: str  # system | operator
    review_deadline: datetime


class HStopRelease(BaseModel):
    reason: str
    released_by: str


class HStopResponse(BaseModel):
    stop_id: str
    h_id: str
    measure: str
    status: str
    scope_target: Optional[str]
    reason: str
    initiated_by: str
    review_deadline: datetime
    released_at: Optional[datetime]
    release_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# --- R-0 Recovery ---

class RecoveryCreate(BaseModel):
    h_id: str
    affected_count: int = 0
    measures: Optional[list] = None
    notes: Optional[str] = None


class RecoveryUpdate(BaseModel):
    status: Optional[str] = None
    measures: Optional[list] = None
    notes: Optional[str] = None


class RecoveryResponse(BaseModel):
    recovery_id: str
    h_id: str
    status: str
    affected_count: int
    measures: Optional[list]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Observe ---

class ObserveLogResponse(BaseModel):
    id: int
    request_id: str
    module: str
    action: str
    target_id: Optional[str]
    actor: Optional[str]
    details: Optional[dict]
    timestamp: datetime

    class Config:
        from_attributes = True
