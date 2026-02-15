from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import requests  # ← use requests instead of httpx

from db import get_db
from schemas.lap_summary import (
    LapSummaryCreate,
    LapSummaryUpdate,
    LapSummaryRead,
)
from services import lap_summary as lap_service


router = APIRouter(prefix="/api/v1/lap_summaries", tags=["lap_summaries"])

@router.post(
    "",
    response_model=LapSummaryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_lap_summary(
    lap_in: LapSummaryCreate,
    db: Session = Depends(get_db),
):
    return lap_service.create_lap_summary(db, lap_in)

@router.post("/import_from_openf1", status_code=status.HTTP_202_ACCEPTED)
def import_lap_summaries(
    session_key: int,
    driver_number: int,
    db: Session = Depends(get_db),
):
    try:
        resp = requests.get(
            "https://api.openf1.org/v1/laps",
            params={"session_key": session_key, "driver_number": driver_number},
            timeout=10,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch from OpenF1: {e}")

    laps = resp.json()

    for lap in laps:
        lap_in = LapSummaryCreate(
            session_key=session_key,
            driver_number=driver_number,
            lap_number=lap["lap_number"],
            lap_duration=lap["lap_duration"],
            max_speed_kph=lap.get("st_speed"),
            avg_speed_kph=None,
            i1_speed=lap.get("i1_speed"),
            i2_speed=lap.get("i2_speed"),
            st_speed=lap.get("st_speed"),
            label=None,
        )
        lap_service.create_lap_summary(db, lap_in) 

    return {"imported": len(laps)}



@router.get("", response_model=List[LapSummaryRead])
def list_lap_summaries(
    session_key: Optional[int] = None,
    driver_number: Optional[int] = None,
    db: Session = Depends(get_db),
):
    return lap_service.list_lap_summaries(db, session_key, driver_number)

@router.get("/{lap_id}", response_model=LapSummaryRead)
def get_lap_summary(lap_id: int, db: Session = Depends(get_db)):
    lap = lap_service.get_lap_summary(db, lap_id)
    if not lap:
        raise HTTPException(status_code=404, detail="Lap summary not found")
    return lap

@router.patch("/{lap_id}", response_model=LapSummaryRead)
def update_lap_summary(
    lap_id: int,
    lap_update: LapSummaryUpdate,
    db: Session = Depends(get_db),
):
    lap = lap_service.update_lap_summary(db, lap_id, lap_update)
    if not lap:
        raise HTTPException(status_code=404, detail="Lap summary not found")
    return lap

@router.delete("/{lap_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lap_summary(lap_id: int, db: Session = Depends(get_db)):
    ok = lap_service.delete_lap_summary(db, lap_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Lap summary not found")
    return None
