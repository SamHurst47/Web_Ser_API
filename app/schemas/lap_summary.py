from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from fastapi import Query

class LapSummaryBase(BaseModel):
    session_key: int
    year: Optional[int] = None
    location: Optional[str] = None
    session_name: Optional[str] = None
    driver_number: int
    lap_number: int
    lap_duration: Optional[float] = None
    
    # --- Add Sector Times ---
    duration_sector_1: Optional[float] = None
    duration_sector_2: Optional[float] = None
    duration_sector_3: Optional[float] = None
    
    # --- Add Pit Booleans ---
    is_pit_out_lap: Optional[bool] = False
    is_pit_in_lap: Optional[bool] = False
    
    max_speed_kph: Optional[float] = None
    avg_speed_kph: Optional[float] = None
    i1_speed: Optional[float] = None
    i2_speed: Optional[float] = None
    st_speed: Optional[float] = None
    label: Optional[str] = None

class LapSummaryCreate(LapSummaryBase):
    pass

class LapSummaryUpdate(BaseModel):
    # allow partial updates to be able to remodel data 
    lap_duration: Optional[float] = Field(None, gt=0)
    max_speed_kph: Optional[float] = Field(None, ge=0)
    avg_speed_kph: Optional[float] = Field(None, ge=0)
    i1_speed: Optional[float] = Field(None, ge=0)
    i2_speed: Optional[float] = Field(None, ge=0)
    st_speed: Optional[float] = Field(None, ge=0)
    label: Optional[str] = None

class LapSummaryRead(LapSummaryBase):
    model_config = ConfigDict(from_attributes=True)

class LapFilter(BaseModel):
    year: Optional[int] = Query(None)  
    location: Optional[str] = Query(None)  
    session_name: Optional[str] = Query(None) 
    driver: Optional[int] = Query(None)