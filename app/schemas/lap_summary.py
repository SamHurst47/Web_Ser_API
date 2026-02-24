from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from fastapi import Query

class LapSummaryBase(BaseModel):
    # Flexible session identifiers (any OR all)
    session_key: Optional[int] = Field(None, ge=1, description="OpenF1 session_key")
    year: Optional[int] = Field(None, ge=1950, le=2030, description="Championship year", examples=[2023])
    location: Optional[str] = Field(None, description="Country/circuit name (fuzzy)", examples=["Belgium"])
    session_name: Optional[str] = Field(None, description="Practice 1, Qualifying, Race", examples=["Qualifying"])
    
    driver_number: int = Field(..., ge=1, le=99)
    lap_number: int = Field(..., ge=1)
    
    lap_duration: Optional[float] = Field(None, gt=0)
    max_speed_kph: Optional[float] = Field(None, ge=0, examples=[320.5])
    avg_speed_kph: Optional[float] = Field(None, ge=0, examples=[210.3])
    i1_speed: Optional[float] = Field(None, ge=0, examples=[295.0])
    i2_speed: Optional[float] = Field(None, ge=0, examples=[305.0])
    st_speed: Optional[float] = Field(None, ge=0, examples=[318.0])
    label: Optional[str] = Field(None, examples=["push"])

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