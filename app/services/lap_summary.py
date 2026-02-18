from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import update, delete, and_, select, true, func
from models import LapSummary
from schemas.lap_summary import (
    LapSummaryCreate,
    LapSummaryUpdate,
    LapFilter,
)
from services.api_converter import get_openf1_session_keys

def create_lap_summary(db: Session, lap_in: LapSummaryCreate) -> LapSummary:
    lap = LapSummary(**lap_in.dict())
    db.add(lap)
    db.commit()
    db.refresh(lap)
    return lap

def list_lap_summaries(
    db: Session,
    session_key: Optional[int] = None,
    meeting_key: Optional[int] = None,
    year: Optional[int] = None,
    location: Optional[str] = None,
    session_name: Optional[str] = None,
    driver_number: Optional[int] = None,
) -> List[LapSummary]:
    q = db.query(LapSummary)

    # If year+location+session_name provided, resolve to session_key
    if year is not None and location is not None and session_name is not None:
        keys = get_openf1_session_keys(year, location, session_name)
        session_key = keys["session_key"]
        meeting_key = keys.get("meeting_key")

    if session_key is not None:
        q = q.filter(LapSummary.session_key == session_key)
    if meeting_key is not None:
        q = q.filter(LapSummary.meeting_key == meeting_key)
    if driver_number is not None:
        q = q.filter(LapSummary.driver_number == driver_number)

    return q.all()

def update_lap_summaries(
    db: Session,
    session_key: Optional[int] = None,
    meeting_key: Optional[int] = None,
    year: Optional[int] = None,
    location: Optional[str] = None,
    session_name: Optional[str] = None,
    driver_number: Optional[int] = None,
    lap_update: LapSummaryUpdate = None,
) -> List[LapSummary]:
    if year is not None and location is not None and session_name is not None:
        keys = get_openf1_session_keys(year, location, session_name)
        session_key = keys["session_key"]

    conditions = []
    if session_key is not None:
        conditions.append(LapSummary.session_key == session_key)
    if driver_number is not None:
        conditions.append(LapSummary.driver_number == driver_number)
    
    if not conditions:
        return []

    # Bulk UPDATE without RETURNING (SQLite-compatible)
    stmt = (
        update(LapSummary)
        .where(and_(*conditions))
        .values(**lap_update.dict(exclude_unset=True))
        .execution_options(synchronize_session=False)
    )
    db.execute(stmt)
    db.commit()

    # Query updated rows back
    q = db.query(LapSummary)
    for cond in conditions:
        q = q.filter(cond)
    return q.all()

def delete_lap_summaries(
    db: Session,
    session_key: Optional[int] = None,
    meeting_key: Optional[int] = None,
    year: Optional[int] = None,
    location: Optional[str] = None,
    session_name: Optional[str] = None,
    driver_number: Optional[int] = None,
) -> int:
    # Resolve session_key if year+location+session_name provided
    if year is not None and location is not None and session_name is not None:
        keys = get_openf1_session_keys(year, location, session_name)
        session_key = keys["session_key"]

    # Build filter conditions
    conditions = []
    if session_key is not None:
        conditions.append(LapSummary.session_key == session_key)
    if driver_number is not None:
        conditions.append(LapSummary.driver_number == driver_number)
    
    if not conditions:
        return 0  # No filters = nothing deleted

    # Bulk DELETE (SQLite-compatible)
    stmt = (
        delete(LapSummary)
        .where(and_(*conditions))
        .execution_options(synchronize_session=False)
    )
    result = db.execute(stmt)
    db.commit()
    return result.rowcount