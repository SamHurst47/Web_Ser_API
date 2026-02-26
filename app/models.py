from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Establish a one-to-many relationship with LapSummary
    lap_summaries = relationship("LapSummary", back_populates="owner", cascade="all, delete-orphan")

class LapSummary(Base):
    __tablename__ = "lap_summaries"

    id = Column(Integer, primary_key=True, index=True)
    
    # 1. The Foreign Key connecting this lap to a specific user
    owner_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    
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

    # 2. The Relationship back to the User
    owner = relationship("Users", back_populates="lap_summaries")