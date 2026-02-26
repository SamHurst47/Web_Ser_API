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

def create_lap_summary(db: Session, lap_in: LapSummaryCreate, owner_id: int) -> LapSummary:
    # 1. Attach the owner_id right when the record is created
    lap = LapSummary(**lap_in.model_dump(), owner_id=owner_id)
    db.add(lap)
    db.commit()
    db.refresh(lap)
    return lap

def list_lap_summaries(
    db: Session,
    owner_id: int,
    session_key: Optional[int] = None,
    meeting_key: Optional[int] = None,
    year: Optional[int] = None,
    location: Optional[str] = None,
    session_name: Optional[str] = None,
    driver_number: Optional[int] = None,
) -> List[LapSummary]:
    q = db.query(LapSummary)

    # 2. Lock the query so it ONLY pulls this user's data
    q = q.filter(LapSummary.owner_id == owner_id)

    # If year+location+session_name provided, resolve to session_key
    if year is not None and location is not None and session_name is not None:
        keys = get_openf1_session_keys(year, location, session_name)
        if keys:
            session_key = keys.get("session_key")
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
    owner_id: int,
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
        if keys:
            session_key = keys.get("session_key")

    # 3. Start the conditions list with the user lock
    conditions = [LapSummary.owner_id == owner_id]
    
    if session_key is not None:
        conditions.append(LapSummary.session_key == session_key)
    if driver_number is not None:
        conditions.append(LapSummary.driver_number == driver_number)
    
    # Require at least one filter besides owner_id to prevent accidental bulk-updates
    if len(conditions) == 1:
        return []

    # Bulk UPDATE without RETURNING (SQLite-compatible)
    stmt = (
        update(LapSummary)
        .where(and_(*conditions))
        .values(**lap_update.model_dump(exclude_unset=True)) # 4. Updated to model_dump!
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
    owner_id: int,
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
        if keys:
            session_key = keys.get("session_key")

    # 5. Build filter conditions starting with the user lock
    conditions = [LapSummary.owner_id == owner_id]
    
    if session_key is not None:
        conditions.append(LapSummary.session_key == session_key)
    if driver_number is not None:
        conditions.append(LapSummary.driver_number == driver_number)
    
    # Require at least one filter besides owner_id to prevent accidental bulk-deletes
    if len(conditions) == 1:
        return 0  

    # Bulk DELETE (SQLite-compatible)
    stmt = (
        delete(LapSummary)
        .where(and_(*conditions))
        .execution_options(synchronize_session=False)
    )
    result = db.execute(stmt)
    db.commit()
    return result.rowcount