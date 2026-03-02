from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional

class LapDataPoint(BaseModel):
    lap_number: int = Field(..., examples=[12])
    lap_duration: float = Field(..., description="Lap time in seconds", examples=[92.455])

class DriverSessionTrend(BaseModel):
    driver_number: int = Field(..., examples=[44])
    session_name: str = Field(..., examples=["Race"])
    laps: List[LapDataPoint]

class PaceTrendResponse(BaseModel):
    year: int = Field(..., examples=[2024])
    location: str = Field(..., examples=["Belgium"])
    trends: List[DriverSessionTrend]

class OverallIdealLap(BaseModel):
    session_name: str = Field(..., examples=["Qualifying"])
    best_sector_1: float = Field(..., examples=[28.123])
    best_sector_2: float = Field(..., examples=[35.456])
    best_sector_3: float = Field(..., examples=[22.890])
    ideal_lap_time: float = Field(..., description="The theoretical best lap", examples=[86.469])

class IdealLapCompare(BaseModel):
    driver_number: int = Field(..., examples=[44])
    session_name: str = Field(..., examples=["Qualifying"])
    ideal_lap_time: Optional[float] = Field(..., examples=[86.750])
    actual_best_lap_time: Optional[float] = Field(..., examples=[87.100])
    potential_improvement: Optional[float] = Field(..., description="The gap between actual best and theoretical best", examples=[0.350])

class IdealLapsResponse(BaseModel):
    year: int = Field(..., examples=[2024])
    location: str = Field(..., examples=["Belgium"])
    overall_ideal_laps: List[OverallIdealLap]
    driver_ideal_laps: List[IdealLapCompare]


class TruePaceCompare(BaseModel):
    driver_number: int = Field(..., description="The unique FIA driver number", examples=[1])
    session_name: str = Field(..., description="The session type", examples=["Race"])
    true_average_pace: float = Field(..., description="Average pace excluding outliers", examples=[109.120])
    valid_laps_counted: int = Field(..., description="Number of representative laps used", examples=[44])
