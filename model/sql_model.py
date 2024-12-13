from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey
from datetime import datetime

BASE = declarative_base()

def get_timestamp(): 
  return datetime.now()
print(get_timestamp())

#creating our model or table
class User(BASE): 
  __tablename__ = 'users'
  __table_args__ = {'schema': 'public'}
  
  id = Column(Integer, primary_key=True, index=True)
  username = Column(String, unique=True, index=True, nullable=False)
  password = Column(String, nullable=False)
  is_admin = Column(Boolean, default=False)
  is_active = Column(Boolean, default=True)

class Satellite(BASE):
  __tablename__ = "satellites"

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, unique=True, nullable=False)
  norad_id = Column(String, unique=True, nullable=False)

  visible_satellites = relationship("VisibleSatellite", backref="satellite", cascade="all, delete-orphan")
  tle = relationship("TLE", back_populates="satellite", cascade="all, delete-orphan")

class VisibleSatellite(BASE):
  __tablename__ = "visible_satellites"

  id = Column(Integer, primary_key=True, index=True)
  satellite_id = Column(Integer, ForeignKey("satellites.id"), nullable=False)  
  visible_at = Column(DateTime, default=datetime.utcnow)


class TLE(BASE):
  __tablename__ = "tle"

  id = Column(Integer, primary_key=True, index=True)
  satellite_id = Column(Integer, ForeignKey("satellites.id"), nullable=False)
  line1 = Column(String, nullable=False)
  line2 = Column(String, nullable=False)
  updated_at = Column(DateTime, default=datetime.utcnow)

  satellite = relationship("Satellite", back_populates="tle")