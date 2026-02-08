"""
HIR MVP — Harm–Integrity–Recovery
Minimum Viable Implementation

Modules: H-Event, H-Stop, R-0, HIR-Observe
Storage: SQLite
API: REST / JSON
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db, init_db, HEvent, HStop, Recovery, ObserveLog
from app.schemas import (
    HEventCreate, HEventStatusUpdate, HEventResponse,
    HStopCreate, HStopRelease, HStopResponse,
    RecoveryCreate, RecoveryUpdate, RecoveryResponse,
    ObserveLogResponse,
)

app = FastAPI(
    title="HIR — Harm–Integrity–Recovery",
    description="MVP: detect, halt, recover. Open protocol for harm accountability.",
    version="0.1.0",
)


@app.on_event("startup")
def startup():
    init_db()


# --- Helpers ---

def generate_h_id(db: Session) -> str:
    year = datetime.now(timezone.utc).year
    count = db.query(HEvent).count() + 1
    return f"HIR-{year}-{count:05d}"


def generate_stop_id(db: Session) -> str:
    year = datetime.now(timezone.utc).year
    count = db.query(HStop).count() + 1
    return f"STOP-{year}-{count:05d}"


def generate_recovery_id(db: Session) -> str:
    year = datetime.now(timezone.utc).year
    count = db.query(Recovery).count() + 1
    return f"R0-{year}-{count:05d}"


def log_action(db: Session, module: str, action: str, target_id: str = None, actor: str = None, details: dict = None):
    entry = ObserveLog(
        request_id=str(uuid.uuid4())[:8],
        module=module,
        action=action,
        target_id=target_id,
        actor=actor,
        details=details,
    )
    db.add(entry)
    db.commit()


# ==========================================
# H-EVENT API
# ==========================================

@app.post("/api/v1/events", response_model=HEventResponse, tags=["H-Event"])
def create_event(event: HEventCreate, db: Session = Depends(get_db)):
    """Register a new harm event. Recording is not accusation — it is fact."""
    h_id = generate_h_id(db)
    db_event = HEvent(
        h_id=h_id,
        harm_type=event.harm_type,
        harm_domain=event.harm_domain,
        description=event.description,
        severity=event.severity,
        confidence=event.confidence,
        affected_scope=event.affected_scope,
        affected_count=event.affected_count,
        horizon=event.horizon,
        source_type=event.source_type,
        source_id=event.source_id,
        metadata_=event.metadata,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    log_action(db, "h_event", "created", h_id, event.source_type, {"severity": event.severity})
    return db_event


@app.get("/api/v1/events/{h_id}", response_model=HEventResponse, tags=["H-Event"])
def get_event(h_id: str, db: Session = Depends(get_db)):
    """Retrieve a harm event by H-ID."""
    event = db.query(HEvent).filter(HEvent.h_id == h_id).first()
    if not event:
        raise HTTPException(status_code=404, detail=f"H-Event {h_id} not found")
    return event


@app.patch("/api/v1/events/{h_id}/status", response_model=HEventResponse, tags=["H-Event"])
def update_event_status(h_id: str, update: HEventStatusUpdate, db: Session = Depends(get_db)):
    """Update the status of a harm event."""
    event = db.query(HEvent).filter(HEvent.h_id == h_id).first()
    if not event:
        raise HTTPException(status_code=404, detail=f"H-Event {h_id} not found")
    old_status = event.status
    event.status = update.status
    event.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(event)
    log_action(db, "h_event", "status_updated", h_id, details={"old": old_status, "new": update.status, "reason": update.reason})
    return event


@app.get("/api/v1/events", response_model=list[HEventResponse], tags=["H-Event"])
def list_events(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List harm events with optional filters."""
    query = db.query(HEvent)
    if status:
        query = query.filter(HEvent.status == status)
    if severity:
        query = query.filter(HEvent.severity == severity)
    return query.order_by(HEvent.created_at.desc()).all()


# ==========================================
# H-STOP API
# ==========================================

@app.post("/api/v1/stop", response_model=HStopResponse, tags=["H-Stop"])
def activate_stop(stop: HStopCreate, db: Session = Depends(get_db)):
    """
    Activate H-Stop: halt harm scaling.
    No irreversible actions. Review deadline is mandatory.
    """
    # Verify H-Event exists
    event = db.query(HEvent).filter(HEvent.h_id == stop.h_id).first()
    if not event:
        raise HTTPException(status_code=404, detail=f"H-Event {stop.h_id} not found")

    stop_id = generate_stop_id(db)
    db_stop = HStop(
        stop_id=stop_id,
        h_id=stop.h_id,
        measure=stop.measure,
        scope_target=stop.scope_target,
        reason=stop.reason,
        initiated_by=stop.initiated_by,
        review_deadline=stop.review_deadline,
    )
    db.add(db_stop)

    # Update event status
    event.status = "h_stop_active"
    event.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(db_stop)
    log_action(db, "h_stop", "activated", stop_id, stop.initiated_by, {"h_id": stop.h_id, "measure": stop.measure})
    return db_stop


@app.post("/api/v1/stop/{stop_id}/release", response_model=HStopResponse, tags=["H-Stop"])
def release_stop(stop_id: str, release: HStopRelease, db: Session = Depends(get_db)):
    """Release H-Stop. Harm scaling halt is lifted."""
    db_stop = db.query(HStop).filter(HStop.stop_id == stop_id).first()
    if not db_stop:
        raise HTTPException(status_code=404, detail=f"H-Stop {stop_id} not found")
    if db_stop.status == "released":
        raise HTTPException(status_code=400, detail=f"H-Stop {stop_id} already released")

    db_stop.status = "released"
    db_stop.released_at = datetime.now(timezone.utc)
    db_stop.release_reason = release.reason

    # Update event status
    event = db.query(HEvent).filter(HEvent.h_id == db_stop.h_id).first()
    if event and event.status == "h_stop_active":
        event.status = "investigating"
        event.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(db_stop)
    log_action(db, "h_stop", "released", stop_id, release.released_by, {"reason": release.reason})
    return db_stop


@app.get("/api/v1/stop", response_model=list[HStopResponse], tags=["H-Stop"])
def list_stops(status: Optional[str] = None, db: Session = Depends(get_db)):
    """List all H-Stops."""
    query = db.query(HStop)
    if status:
        query = query.filter(HStop.status == status)
    return query.order_by(HStop.created_at.desc()).all()


# ==========================================
# R-0 RECOVERY API
# ==========================================

@app.post("/api/v1/recovery", response_model=RecoveryResponse, tags=["R-0 Recovery"])
def initiate_recovery(recovery: RecoveryCreate, db: Session = Depends(get_db)):
    """
    Initiate R-0: immediate recovery.
    Recovery starts BEFORE investigation, BEFORE blame, BEFORE sanctions.
    """
    # Verify H-Event exists
    event = db.query(HEvent).filter(HEvent.h_id == recovery.h_id).first()
    if not event:
        raise HTTPException(status_code=404, detail=f"H-Event {recovery.h_id} not found")

    recovery_id = generate_recovery_id(db)
    db_recovery = Recovery(
        recovery_id=recovery_id,
        h_id=recovery.h_id,
        affected_count=recovery.affected_count,
        measures=recovery.measures,
        notes=recovery.notes,
    )
    db.add(db_recovery)

    # Update event status
    event.status = "recovering"
    event.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(db_recovery)
    log_action(db, "r0", "initiated", recovery_id, details={"h_id": recovery.h_id, "affected": recovery.affected_count})
    return db_recovery


@app.patch("/api/v1/recovery/{recovery_id}", response_model=RecoveryResponse, tags=["R-0 Recovery"])
def update_recovery(recovery_id: str, update: RecoveryUpdate, db: Session = Depends(get_db)):
    """Update recovery status or measures."""
    db_recovery = db.query(Recovery).filter(Recovery.recovery_id == recovery_id).first()
    if not db_recovery:
        raise HTTPException(status_code=404, detail=f"Recovery {recovery_id} not found")

    if update.status:
        db_recovery.status = update.status
    if update.measures:
        db_recovery.measures = update.measures
    if update.notes:
        db_recovery.notes = update.notes
    db_recovery.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(db_recovery)
    log_action(db, "r0", "updated", recovery_id, details={"status": update.status})
    return db_recovery


@app.get("/api/v1/recovery", response_model=list[RecoveryResponse], tags=["R-0 Recovery"])
def list_recoveries(status: Optional[str] = None, db: Session = Depends(get_db)):
    """List all recoveries."""
    query = db.query(Recovery)
    if status:
        query = query.filter(Recovery.status == status)
    return query.order_by(Recovery.created_at.desc()).all()


# ==========================================
# HIR-OBSERVE API
# ==========================================

@app.get("/api/v1/observe/logs", response_model=list[ObserveLogResponse], tags=["HIR-Observe"])
def get_logs(
    module: Optional[str] = None,
    target_id: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db),
):
    """Retrieve system logs. Every action is traceable."""
    query = db.query(ObserveLog)
    if module:
        query = query.filter(ObserveLog.module == module)
    if target_id:
        query = query.filter(ObserveLog.target_id == target_id)
    return query.order_by(ObserveLog.timestamp.desc()).limit(limit).all()


@app.get("/api/v1/observe/stats", tags=["HIR-Observe"])
def get_stats(db: Session = Depends(get_db)):
    """System statistics overview."""
    return {
        "total_events": db.query(HEvent).count(),
        "active_stops": db.query(HStop).filter(HStop.status == "active").count(),
        "active_recoveries": db.query(Recovery).filter(Recovery.status.in_(["initiated", "in_progress"])).count(),
        "events_by_severity": {
            "critical": db.query(HEvent).filter(HEvent.severity == "critical").count(),
            "high": db.query(HEvent).filter(HEvent.severity == "high").count(),
            "medium": db.query(HEvent).filter(HEvent.severity == "medium").count(),
            "low": db.query(HEvent).filter(HEvent.severity == "low").count(),
        },
        "events_by_status": {
            "registered": db.query(HEvent).filter(HEvent.status == "registered").count(),
            "h_stop_active": db.query(HEvent).filter(HEvent.status == "h_stop_active").count(),
            "recovering": db.query(HEvent).filter(HEvent.status == "recovering").count(),
            "resolved": db.query(HEvent).filter(HEvent.status == "resolved").count(),
        },
    }


# ==========================================
# ROOT
# ==========================================

@app.get("/", tags=["System"])
def root():
    return {
        "system": "HIR — Harm–Integrity–Recovery",
        "version": "0.1.0-mvp",
        "principle": "Recovery before blame. Halt before discussion. Record before judgment.",
        "docs": "/docs",
        "author": "Artem Bykov (Kech)",
        "license": "CC BY-SA 4.0",
        "repository": "github.com/artemzkech-code/HIR",
        "doi": "10.5281/zenodo.18528379",
    }

