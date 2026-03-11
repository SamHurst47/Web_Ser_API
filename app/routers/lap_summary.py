from typing import List, Optional
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import requests  

from db import get_db
from models import Users 
from services.dependencies import get_current_user 
from schemas.lap_summary import LapSummaryCreate, LapSummaryUpdate, LapSummaryRead, ImportResponse
from services import lap_summary as lap_service
from services.api_converter import get_openf1_session_keys 

# Define an Enum for cleaner UI dropdowns
class SessionName(str, Enum):
    race = "Race"
    qualifying = "Qualifying"
    sprint = "Sprint"
    p1 = "Practice 1"
    p2 = "Practice 2"
    p3 = "Practice 3"

router = APIRouter(prefix="/api/v1/lap_summaries", tags=["Lap Summaries"])

@router.post(
    "/import_from_openf1", 
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ImportResponse,
    summary="Import Telemetry from OpenF1"
)
def import_lap_summaries(
    driver_number: int = Query(..., description="FIA Driver Number", examples=[1, 44, 16]),
    year: Optional[int] = Query(None, description="The four-digit race year", examples=[2023, 2024]),
    location: Optional[str] = Query(None, description="Grand Prix location", examples=["Belgium", "Italy", "Silverstone"]),
    session_name: Optional[SessionName] = Query(None, description="Session type"),
    session_key: Optional[int] = Query(None, description="Direct OpenF1 Session Key", examples=[9141, 9158]),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Fetches lap data from OpenF1 and saves it. 
    Providing Year/Location/Session name automatically resolves the session_key.
    """
    if location: location = location.strip()
    
    # Extract string from Enum if provided
    sess_str = session_name.value if session_name else None

    if year is not None and location is not None and sess_str is not None:
        keys = get_openf1_session_keys(year, location, sess_str)
        if keys is None:
            raise HTTPException(status_code=422, detail="Invalid session parameters provided")
        session_key = keys["session_key"]
    elif not session_key:
        raise HTTPException(400, "Must provide session_key OR year, location, and session_name")
    
    try:
        resp = requests.get(
            "https://api.openf1.org/v1/laps",
            params={"session_key": session_key, "driver_number": driver_number},
            timeout=10,
        )
        resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"OpenF1 fetch failed: {e}")

    laps = resp.json()
    imported_count = 0
    
    for lap in laps:
        lap_in = LapSummaryCreate(
            session_key=session_key,
            year=year, 
            location=location, 
            session_name=sess_str,
            driver_number=driver_number, 
            lap_number=lap["lap_number"],
            lap_duration=lap.get("lap_duration"), 
            duration_sector_1=lap.get("duration_sector_1"),
            duration_sector_2=lap.get("duration_sector_2"),
            duration_sector_3=lap.get("duration_sector_3"),
            is_pit_out_lap=lap.get("is_pit_out_lap", False),
            is_pit_in_lap=lap.get("is_pit_in_lap", False),
            max_speed_kph=lap.get("st_speed"), 
            i1_speed=lap.get("i1_speed"),
            i2_speed=lap.get("i2_speed"), 
            st_speed=lap.get("st_speed"), 
            label=None,
        )
        lap_service.create_lap_summary(db, lap_in, owner_id=current_user.id)
        imported_count += 1

    return {"imported": imported_count, "session_key": session_key}

@router.get(
    "", 
    response_model=List[LapSummaryRead],
    summary="List Saved Lap Summaries"
)
def list_lap_summaries(
    session_key: Optional[int] = Query(None, examples=[9141]),
    year: Optional[int] = Query(None, examples=[2023]),
    location: Optional[str] = Query(None, examples=["Belgium", "Italy"]),
    session_name: Optional[SessionName] = Query(None),
    driver_number: Optional[int] = Query(None, examples=[1, 44]),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user) 
):
    sess_str = session_name.value if session_name else None
    return lap_service.list_lap_summaries(
        db, current_user.id, session_key, None, year, location, sess_str, driver_number
    )

@router.put(
    "", 
    response_model=List[LapSummaryRead],
    summary="Update Existing Summaries"
)
def update_lap_summaries(
    driver_number: int = Query(..., examples=[44]),
    lap_update: LapSummaryUpdate = None,
    session_key: Optional[int] = Query(None, examples=[9141]),
    year: Optional[int] = Query(None, examples=[2023]),
    location: Optional[str] = Query(None, examples=["Belgium"]),
    session_name: Optional[SessionName] = Query(None),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    sess_str = session_name.value if session_name else None
    updated = lap_service.update_lap_summaries(
        db, current_user.id, session_key, None, year, location, sess_str, driver_number, lap_update
    )
    if not updated:
        raise HTTPException(status_code=404, detail="No matching laps found to update")
    return updated

@router.delete(
    "", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Summaries"
)
def delete_lap_summaries(
    driver_number: int = Query(..., examples=[44]),
    session_key: Optional[int] = Query(None, examples=[9141]),
    year: Optional[int] = Query(None, examples=[2023]),
    location: Optional[str] = Query(None, examples=["Belgium"]),
    session_name: Optional[SessionName] = Query(None),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user) 
):
    sess_str = session_name.value if session_name else None
    count = lap_service.delete_lap_summaries(
        db, current_user.id, session_key, None, year, location, sess_str, driver_number
    )
    if count == 0:
        raise HTTPException(status_code=404, detail="No matching laps found to delete")
    return None