from sqlalchemy.orm import Session
from sqlalchemy import asc, func
from models import LapSummary
from typing import List, Optional

def get_pace_trend(
    db: Session, owner_id: int, year: int, location: str, 
    session_name: Optional[str] = None, driver_numbers: Optional[List[int]] = None
):
    query = db.query(LapSummary).filter(
        LapSummary.owner_id == owner_id,
        LapSummary.year == year,
        LapSummary.location == location,
        LapSummary.lap_duration.isnot(None)
    )
    if session_name: query = query.filter(LapSummary.session_name == session_name)
    
    # FIX: Safely check that the list actually has items before filtering
    if driver_numbers and len(driver_numbers) > 0: 
        query = query.filter(LapSummary.driver_number.in_(driver_numbers))

    return query.order_by(LapSummary.session_name, LapSummary.driver_number, asc(LapSummary.lap_number)).all()

def get_overall_ideal_laps(
    db: Session, owner_id: int, year: int, location: str, session_name: Optional[str] = None
):
    # Calculates the absolute best sectors across ALL drivers
    query = db.query(
        LapSummary.session_name,
        func.min(LapSummary.duration_sector_1).label('best_s1'),
        func.min(LapSummary.duration_sector_2).label('best_s2'),
        func.min(LapSummary.duration_sector_3).label('best_s3')
    ).filter(
        LapSummary.owner_id == owner_id,
        LapSummary.year == year,
        LapSummary.location == location
    )
    if session_name: query = query.filter(LapSummary.session_name == session_name)
    
    return query.group_by(LapSummary.session_name).all()

def get_ideal_laps_grouped(
    db: Session, owner_id: int, year: int, location: str, 
    session_name: Optional[str] = None, driver_numbers: Optional[List[int]] = None
):
    query = db.query(
        LapSummary.driver_number,
        LapSummary.session_name,
        func.min(LapSummary.duration_sector_1).label('best_s1'),
        func.min(LapSummary.duration_sector_2).label('best_s2'),
        func.min(LapSummary.duration_sector_3).label('best_s3'),
        func.min(LapSummary.lap_duration).label('actual_best')
    ).filter(
        LapSummary.owner_id == owner_id,
        LapSummary.year == year,
        LapSummary.location == location
    )
    if session_name: query = query.filter(LapSummary.session_name == session_name)
    if driver_numbers and len(driver_numbers) > 0: 
        query = query.filter(LapSummary.driver_number.in_(driver_numbers))

    return query.group_by(LapSummary.driver_number, LapSummary.session_name).all()

def get_true_pace_grouped(
    db: Session, owner_id: int, year: int, location: str, 
    session_name: Optional[str] = None, driver_numbers: Optional[List[int]] = None
):
    query = db.query(
        LapSummary.driver_number,
        LapSummary.session_name,
        func.avg(LapSummary.lap_duration).label('avg_pace'),
        func.count(LapSummary.id).label('lap_count')
    ).filter(
        LapSummary.owner_id == owner_id,
        LapSummary.year == year,
        LapSummary.location == location,
        LapSummary.lap_duration.isnot(None),
        LapSummary.is_pit_in_lap == False,
        LapSummary.is_pit_out_lap == False
    )
    if session_name: query = query.filter(LapSummary.session_name == session_name)
    if driver_numbers and len(driver_numbers) > 0: 
        query = query.filter(LapSummary.driver_number.in_(driver_numbers))

    return query.group_by(LapSummary.driver_number, LapSummary.session_name).all()