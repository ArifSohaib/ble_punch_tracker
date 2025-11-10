from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base

class WorkoutSession(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True, index=True)
    start_time = Column(DateTime, default=datetime.now())
    end_time = Column(DateTime, nullable=True)
    readings = relationship("Reading", back_populates="session")

class Reading(Base):
    __tablename__ = "readings"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    timestamp = Column(DateTime, default=datetime.now())
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)
    session = relationship("WorkoutSession", back_populates="readings")
