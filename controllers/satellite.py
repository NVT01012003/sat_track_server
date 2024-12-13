from model.sql_model import Satellite
from sqlalchemy.orm import Session
from typing import Optional

# CRUD cho Satellite
def create_satellite(db: Session, name: str, norad_id: str):
    db_satellite = Satellite(name=name, norad_id=norad_id)
    db.add(db_satellite)
    db.commit()
    db.refresh(db_satellite)
    return db_satellite

def get_satellite(db: Session, satellite_id: int):
    return db.query(Satellite).filter(Satellite.id == satellite_id).first()

def get_satellites(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Satellite).offset(skip).limit(limit).all()

def update_satellite(db: Session, satellite_id: int, name: Optional[str] = None, norad_id: Optional[str] = None):
    db_satellite = db.query(Satellite).filter(Satellite.id == satellite_id).first()
    if db_satellite:
        if name:
            db_satellite.name = name
        if norad_id:
            db_satellite.norad_id = norad_id
        db.commit()
        db.refresh(db_satellite)
    return db_satellite

def delete_satellite(db: Session, satellite_id: int):
    db_satellite = db.query(Satellite).filter(Satellite.id == satellite_id).first()
    if db_satellite:
        db.delete(db_satellite)
        db.commit()
    return db_satellite
