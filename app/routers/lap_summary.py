from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import requests  
from services.api_converter import get_openf1_session_keys 

from db import get_db
from models import Users # Import the User model
from services.dependencies import get_current_user # Import our new security lock!
from schemas.lap_summary import LapSummaryCreate, LapSummaryUpdate, LapSummaryRead
from services import lap_summary as lap_service

router = APIRouter(prefix="/api/v1/lap_summaries", tags=["lap_summaries"])

@router.post("/import_from_openf1", status_code=status.HTTP_202_ACCEPTED)
def import_lap_summaries(
    driver_number: int,
    year: Optional[int] = Query(None),
    location: Optional[str] = Query(None),
    session_name: Optional[str] = Query(None),
    session_key: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user) # <-- Lock added!
):
    # Sanitize inputs
    if location: location = location.strip()
    if session_name: session_name = session_name.strip()

    if year is not None and location is not None and session_name is not None:
        keys = get_openf1_session_keys(year, location, session_name)
        if keys is None:
            raise HTTPException(status_code=422, detail="Invalid session input")
        session_key = keys["session_key"]
    elif not session_key:
        raise HTTPException(400, "Provide session_key OR (year+location+session_name)")
    
    try:
        resp = requests.get(
            "https://api.openf1.org/v1/laps",
            params={"session_key": session_key, "driver_number": driver_number},
            timeout=10,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"OpenF1 fetch failed: {e}")

    laps = resp.json()
    imported_count = 0
    
    for lap in laps:
        lap_in = LapSummaryCreate(
            session_key=session_key,
            year=year, location=location, session_name=session_name,
            driver_number=driver_number, lap_number=lap["lap_number"],
            lap_duration=lap.get("lap_duration"), max_speed_kph=lap.get("st_speed"),
            avg_speed_kph=None, i1_speed=lap.get("i1_speed"),
            i2_speed=lap.get("i2_speed"), st_speed=lap.get("st_speed"), label=None,
        )
        # Pass the current_user.id down to the service!
        lap_service.create_lap_summary(db, lap_in, owner_id=current_user.id)
        imported_count += 1

    return {"imported": imported_count, "session_key": session_key}

@router.get("", response_model=List[LapSummaryRead])
def list_lap_summaries(
    session_key: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    location: Optional[str] = Query(None),
    session_name: Optional[str] = Query(None),
    driver_number: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user) 
):
    return lap_service.list_lap_summaries(
        db, current_user.id, session_key, None, year, location, session_name, driver_number
    )

@router.put("", response_model=List[LapSummaryRead])
def update_lap_summaries(
    driver_number: int,
    lap_update: LapSummaryUpdate,
    session_key: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    location: Optional[str] = Query(None),
    session_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    updated = lap_service.update_lap_summaries(
        db, current_user.id, session_key, None, year, location, session_name, driver_number, lap_update
    )
    if not updated:
        raise HTTPException(status_code=404, detail="No laps matched filters")
    return updated

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_lap_summaries(
    driver_number: int,
    session_key: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    location: Optional[str] = Query(None),
    session_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user) 
):
    count = lap_service.delete_lap_summaries(
        db, current_user.id, session_key, None, year, location, session_name, driver_number
    )
    if count == 0:
        raise HTTPException(status_code=404, detail="No laps matched filters")
    return None