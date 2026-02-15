from typing import List, Optional
from sqlalchemy.orm import Session
from models import LapSummary
from schemas.lap_summary import (
    LapSummaryCreate,
    LapSummaryUpdate,
)

def create_lap_summary(db: Session, lap_in: LapSummaryCreate) -> LapSummary:
    lap = LapSummary(**lap_in.dict())
    db.add(lap)
    db.commit()
    db.refresh(lap)
    return lap

def list_lap_summaries(
    db: Session,
    session_key: Optional[int] = None,
    driver_number: Optional[int] = None,
) -> List[LapSummary]:
    q = db.query(LapSummary)
    if session_key is not None:
        q = q.filter(LapSummary.session_key == session_key)
    if driver_number is not None:
        q = q.filter(LapSummary.driver_number == driver_number)
    return q.all()

def get_lap_summary(db: Session, lap_id: int) -> Optional[LapSummary]:
    return db.query(LapSummary).get(lap_id)

def update_lap_summary(
    db: Session, lap_id: int, lap_update: LapSummaryUpdate
) -> Optional[LapSummary]:
    lap = db.query(LapSummary).get(lap_id)
    if not lap:
        return None
    data = lap_update.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(lap, field, value)
    db.commit()
    db.refresh(lap)
    return lap

def delete_lap_summary(db: Session, lap_id: int) -> bool:
    lap = db.query(LapSummary).get(lap_id)
    if not lap:
        return False
    db.delete(lap)
    db.commit()
    return True
