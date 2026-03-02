from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from db import get_db
from models import Users
from services.dependencies import get_current_user
from schemas.analytics import PaceTrendResponse, IdealLapsResponse, IdealLapCompare, OverallIdealLap, TruePaceCompare, DriverSessionTrend
from services import analytics as analytics_service

router = APIRouter(prefix="/api/v1/analytics", tags=["Data Analytics"])

@router.get(
    "/pace-trend", 
    response_model=PaceTrendResponse,
    summary="Get Driver Pace Trends",
    description="Returns a chronological list of lap times for one or more drivers to visualize pace evolution over a session."
)
def get_pace_trend(
    year: int = Query(..., examples=2023), 
    location: str = Query(..., examples="Belgium"),
    session_name: Optional[str] = Query(None, examples="Race"),
    driver_numbers: Optional[List[int]] = Query(None, examples=[44, 63]),
    db: Session = Depends(get_db), 
    current_user: Users = Depends(get_current_user)
):
    laps = analytics_service.get_pace_trend(db, current_user.id, year, location, session_name, driver_numbers)
    
    grouped_data = {}
    for lap in laps:
        key = (lap.driver_number, lap.session_name)
        if key not in grouped_data: grouped_data[key] = []
        grouped_data[key].append({"lap_number": lap.lap_number, "lap_duration": lap.lap_duration})

    trends = [DriverSessionTrend(driver_number=d, session_name=s, laps=l) for (d, s), l in grouped_data.items()]
    return PaceTrendResponse(year=year, location=location, trends=trends)

@router.get(
    "/ideal-laps", 
    response_model=IdealLapsResponse,
    summary="Theoretical Ideal Lap Analysis",
    description="""
Calculates the 'Ideal Lap' (the sum of the best individual sectors) for the session as a whole 
and for individual drivers. This identifies the 'Potential Improvement' left on the table.
    """
)
def get_ideal_laps(
    year: int = Query(..., examples=2023), 
    location: str = Query(..., examples="Belgium"),
    session_name: Optional[str] = Query(None, examples="Race"),
    driver_numbers: Optional[List[int]] = Query(None, examples=[4, 81]),
    db: Session = Depends(get_db), 
    current_user: Users = Depends(get_current_user)
):
    overall_results = analytics_service.get_overall_ideal_laps(db, current_user.id, year, location, session_name)
    overall_laps = []
    for row in overall_results:
        if row.best_s1 and row.best_s2 and row.best_s3:
            overall_laps.append(OverallIdealLap(
                session_name=row.session_name,
                best_sector_1=round(row.best_s1, 3),
                best_sector_2=round(row.best_s2, 3),
                best_sector_3=round(row.best_s3, 3),
                ideal_lap_time=round(row.best_s1 + row.best_s2 + row.best_s3, 3)
            ))

    driver_results = analytics_service.get_ideal_laps_grouped(db, current_user.id, year, location, session_name, driver_numbers)
    driver_laps = []
    for row in driver_results:
        if row.best_s1 and row.best_s2 and row.best_s3:
            ideal = round(row.best_s1 + row.best_s2 + row.best_s3, 3)
            actual = round(row.actual_best, 3) if row.actual_best else None
            diff = round(actual - ideal, 3) if actual else None
            
            driver_laps.append(IdealLapCompare(
                driver_number=row.driver_number, session_name=row.session_name,
                ideal_lap_time=ideal, actual_best_lap_time=actual, potential_improvement=diff
            ))
            
    return IdealLapsResponse(year=year, location=location, overall_ideal_laps=overall_laps, driver_ideal_laps=driver_laps)

@router.get(
    "/true-pace", 
    response_model=List[TruePaceCompare],
    summary="True Average Pace",
    description="Calculates the average pace per driver, filtering out non-representative laps (pits/out-laps) to show pure performance."
)
def get_true_pace(
    year: int = Query(..., examples=2023), 
    location: str = Query(..., examples="Belgium"),
    session_name: Optional[str] = Query(None, examples="Race"),
    driver_numbers: Optional[List[int]] = Query(None, examples=[1, 11]),
    db: Session = Depends(get_db), 
    current_user: Users = Depends(get_current_user)
):
    results = analytics_service.get_true_pace_grouped(db, current_user.id, year, location, session_name, driver_numbers)
    return [
        TruePaceCompare(
            driver_number=row.driver_number, session_name=row.session_name,
            true_average_pace=round(row.avg_pace, 3), valid_laps_counted=row.lap_count
        ) for row in results if row.avg_pace
    ]