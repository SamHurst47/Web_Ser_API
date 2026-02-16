from sqlalchemy import Column, Integer, String, Float
from db import Base

class LapSummary(Base):
    __tablename__ = "lap_summaries"

    id = Column(Integer, primary_key=True, index=True)
    session_key = Column(Integer, index=True, nullable=False)
    year = Column(Integer, index=True, nullable=True)        
    location = Column(String, index=True, nullable=True)
    session_name = Column(String, index=True, nullable=True)
    
    driver_number = Column(Integer, index=True, nullable=False)
    lap_number = Column(Integer, nullable=False)
    lap_duration = Column(Float, nullable=True)
    max_speed_kph = Column(Float, nullable=True)
    avg_speed_kph = Column(Float, nullable=True)
    i1_speed = Column(Float, nullable=True)
    i2_speed = Column(Float, nullable=True)
    st_speed = Column(Float, nullable=True)
    label = Column(String, nullable=True)
