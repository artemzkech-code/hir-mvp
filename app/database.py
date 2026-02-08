"""HIR MVP — Database models and connection."""

from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, JSON, Enum as SAEnum
from sqlalchemy.orm import declarative_base, sessionmaker
import enum

DATABASE_URL = "sqlite:///./hir.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Enums ---

class HarmType(str, enum.Enum):
    direct = "direct"
    indirect = "indirect"
    systemic = "systemic"
    deferred = "deferred"


class Severity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Confidence(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    confirmed = "confirmed"


class EventStatus(str, enum.Enum):
    registered = "registered"
    investigating = "investigating"
    h_stop_active = "h_stop_active"
    recovering = "recovering"
    resolved = "resolved"
    disputed = "disputed"
    false_positive = "false_positive"


class StopMeasure(str, enum.Enum):
    pause = "pause"
    rate_limit = "rate_limit"
    scope_reduction = "scope_reduction"
    manual_mode = "manual_mode"


class StopStatus(str, enum.Enum):
    active = "active"
    released = "released"
    extended = "extended"


class RecoveryStatus(str, enum.Enum):
    initiated = "initiated"
    in_progress = "in_progress"
    completed = "completed"
    declined = "declined"


# --- Database Tables ---

class HEvent(Base):
    __tablename__ = "h_events"

    h_id = Column(String, primary_key=True)
    status = Column(String, default=EventStatus.registered.value)
    harm_type = Column(String)
    harm_domain = Column(String)
    description = Column(Text)
    severity = Column(String)
    confidence = Column(String)
    affected_scope = Column(String, default="individual")
    affected_count = Column(Integer, nullable=True)
    horizon = Column(String, default="immediate")
    source_type = Column(String)
    source_id = Column(String, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class HStop(Base):
    __tablename__ = "h_stops"

    stop_id = Column(String, primary_key=True)
    h_id = Column(String)
    measure = Column(String)
    status = Column(String, default=StopStatus.active.value)
    scope_target = Column(String, nullable=True)
    reason = Column(Text)
    initiated_by = Column(String)
    review_deadline = Column(DateTime)
    released_at = Column(DateTime, nullable=True)
    release_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Recovery(Base):
    __tablename__ = "recoveries"

    recovery_id = Column(String, primary_key=True)
    h_id = Column(String)
    status = Column(String, default=RecoveryStatus.initiated.value)
    affected_count = Column(Integer, default=0)
    measures = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ObserveLog(Base):
    __tablename__ = "observe_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String)
    module = Column(String)
    action = Column(String)
    target_id = Column(String, nullable=True)
    actor = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db():
    Base.metadata.create_all(bind=engine)
