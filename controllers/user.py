from model.sql_model import User
from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException

def create_user(db: Session, username: str, password: str, is_admin: bool = False, is_active: bool = True):
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = User(username=username, password=password, is_admin=is_admin, is_active=is_active)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, username: Optional[str] = None, password: Optional[str] = None, is_admin: Optional[bool] = None, is_active: Optional[bool] = None):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        if username:
            db_user.username = username
        if password:
            db_user.password = password
        if is_admin is not None:
            db_user.is_admin = is_admin
        if is_active is not None:
            db_user.is_active = is_active
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user