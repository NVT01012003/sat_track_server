from model.sql_model import VisibleSatellite
from sqlalchemy.orm import Session
from typing import Optional

def create_visible_satellite(db: Session, satellite_id: int, visible_at: datetime = datetime.utcnow()):
    db_visible_satellite = VisibleSatellite(satellite_id=satellite_id, visible_at=visible_at)
    db.add(db_visible_satellite)
    db.commit()
    db.refresh(db_visible_satellite)
    return db_visible_satellite

def get_visible_satellite(db: Session, visible_satellite_id: int):
    return db.query(VisibleSatellite).filter(VisibleSatellite.id == visible_satellite_id).first()

def get_visible_satellites(db: Session, skip: int = 0, limit: int = 100):
    return db.query(VisibleSatellite).offset(skip).limit(limit).all()

def update_visible_satellite(db: Session, visible_satellite_id: int, visible_at: Optional[datetime] = None):
    db_visible_satellite = db.query(VisibleSatellite).filter(VisibleSatellite.id == visible_satellite_id).first()
    if db_visible_satellite:
        if visible_at:
            db_visible_satellite.visible_at = visible_at
        db.commit()
        db.refresh(db_visible_satellite)
    return db_visible_satellite

def delete_visible_satellite(db: Session, visible_satellite_id: int):
    db_visible_satellite = db.query(VisibleSatellite).filter(VisibleSatellite.id == visible_satellite_id).first()
    if db_visible_satellite:
        db.delete(db_visible_satellite)
        db.commit()
    return db_visible_satellite