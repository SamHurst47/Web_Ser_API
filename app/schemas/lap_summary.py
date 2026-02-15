from typing import Optional
from pydantic import BaseModel, Field

from typing import Optional

class LapSummaryBase(BaseModel):
    session_key: int
    driver_number: int
    lap_number: int = Field(..., ge=1)
    lap_duration: Optional[float] = Field(None, gt=0)
    max_speed_kph: Optional[float] = Field(None, ge=0, example=320.5)
    avg_speed_kph: Optional[float] = Field(None, ge=0, example=210.3)
    i1_speed: Optional[float] = Field(None, ge=0, example=295.0)
    i2_speed: Optional[float] = Field(None, ge=0, example=305.0)
    st_speed: Optional[float] = Field(None, ge=0, example=318.0)
    label: Optional[str] = Field(None, example="push")

class LapSummaryCreate(LapSummaryBase):
    pass

class LapSummaryUpdate(BaseModel):
    # allow partial updates
    lap_duration: Optional[float] = Field(None, gt=0)
    max_speed_kph: Optional[float] = Field(None, ge=0)
    avg_speed_kph: Optional[float] = Field(None, ge=0)
    i1_speed: Optional[float] = Field(None, ge=0)
    i2_speed: Optional[float] = Field(None, ge=0)
    st_speed: Optional[float] = Field(None, ge=0)
    label: Optional[str] = None

class LapSummaryRead(LapSummaryBase):
    id: int

    class Config:
        orm_mode = True
