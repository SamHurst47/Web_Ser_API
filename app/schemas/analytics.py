from pydantic import BaseModel
from typing import List, Optional

class LapDataPoint(BaseModel):
    lap_number: int
    lap_duration: float

class DriverSessionTrend(BaseModel):
    driver_number: int
    session_name: str
    laps: List[LapDataPoint]

class PaceTrendResponse(BaseModel):
    year: int
    location: str
    trends: List[DriverSessionTrend]

class OverallIdealLap(BaseModel):
    session_name: str
    best_sector_1: float
    best_sector_2: float
    best_sector_3: float
    ideal_lap_time: float

class IdealLapCompare(BaseModel):
    driver_number: int
    session_name: str
    ideal_lap_time: Optional[float]
    actual_best_lap_time: Optional[float]
    potential_improvement: Optional[float]

class IdealLapsResponse(BaseModel):
    year: int
    location: str
    overall_ideal_laps: List[OverallIdealLap]
    driver_ideal_laps: List[IdealLapCompare]

class TruePaceCompare(BaseModel):
    driver_number: int
    session_name: str
    true_average_pace: float
    valid_laps_counted: int