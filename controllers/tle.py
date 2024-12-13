from model.sql_model import TLE
from sqlalchemy.orm import Session
from typing import Optional

def create_tle(db: Session, satellite_id: int, line1: str, line2: str):
    db_tle = TLE(satellite_id=satellite_id, line1=line1, line2=line2)
    db.add(db_tle)
    db.commit()
    db.refresh(db_tle)
    return db_tle

def get_tle(db: Session, tle_id: int):
    return db.query(TLE).filter(TLE.id == tle_id).first()

def get_tles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(TLE).offset(skip).limit(limit).all()

def update_tle(db: Session, tle_id: int, line1: Optional[str] = None, line2: Optional[str] = None):
    db_tle = db.query(TLE).filter(TLE.id == tle_id).first()
    if db_tle:
        if line1:
            db_tle.line1 = line1
        if line2:
            db_tle.line2 = line2
        db.commit()
        db.refresh(db_tle)
    return db_tle

def delete_tle(db: Session, tle_id: int):
    db_tle = db.query(TLE).filter(TLE.id == tle_id).first()
    if db_tle:
        db.delete(db_tle)
        db.commit()
    return db_tle