from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from fastapi import Query

class LapSummaryBase(BaseModel):
    session_key: int = Field(..., examples=[9141])
    year: Optional[int] = Field(None, examples=[2023])
    location: Optional[str] = Field(None, examples=["Belgium"])
    session_name: Optional[str] = Field(None, examples=["Race"])
    driver_number: int = Field(..., examples=[1])
    lap_number: int = Field(..., examples=[1])
    lap_duration: Optional[float] = Field(None, examples=[107.540])
    
    duration_sector_1: Optional[float] = Field(None, examples=[30.450])
    duration_sector_2: Optional[float] = Field(None, examples=[48.120])
    duration_sector_3: Optional[float] = Field(None, examples=[28.970])
    
    is_pit_out_lap: Optional[bool] = Field(False, examples=[False])
    is_pit_in_lap: Optional[bool] = Field(False, examples=[False])
    
    max_speed_kph: Optional[float] = Field(None, examples=[315.5])
    avg_speed_kph: Optional[float] = Field(None, examples=[234.2])
    i1_speed: Optional[float] = Field(None, examples=[280.0])
    i2_speed: Optional[float] = Field(None, examples=[305.0])
    st_speed: Optional[float] = Field(None, examples=[315.0])
    label: Optional[str] = Field(None, examples=["Fastest Lap"])

class ImportResponse(BaseModel):
    # Fixed: examples must be a list []
    imported: int = Field(..., description="The number of laps successfully saved", examples=[44])
    session_key: int = Field(..., description="The OpenF1 Session Key used for the import", examples=[9141])

class LapSummaryCreate(LapSummaryBase):
    pass

class LapSummaryUpdate(BaseModel):
    # allow partial updates to be able to remodel data 
    lap_duration: Optional[float] = Field(None, gt=0, examples=[106.900])
    max_speed_kph: Optional[float] = Field(None, ge=0, examples=[320.0])
    avg_speed_kph: Optional[float] = Field(None, ge=0)
    i1_speed: Optional[float] = Field(None, ge=0)
    i2_speed: Optional[float] = Field(None, ge=0)
    st_speed: Optional[float] = Field(None, ge=0)
    label: Optional[str] = Field(None, examples=["Remodeled Data"])

class LapSummaryRead(LapSummaryBase):
    model_config = ConfigDict(from_attributes=True)

class LapFilter(BaseModel):
    year: Optional[int] = Query(None, examples=[2023])  
    location: Optional[str] = Query(None, examples=["Belgium"])  
    session_name: Optional[str] = Query(None, examples=["Race"]) 
    driver: Optional[int] = Query(None, examples=[1])