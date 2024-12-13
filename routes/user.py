# routes/user.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from controllers.user import create_user, get_user, get_users, update_user, delete_user, get_user_by_username
from connection import get_db
from schemas.user import *

router = APIRouter()

@router.post("/", response_model=User)
def create_user_r(user: UserCreate, db: Session = Depends(get_db)):
    # print({"username": user.username, "password": user.password})
    return create_user(db=db, username=user.username, password=user.password, is_admin=False, is_active=True)

@router.get("/", response_model=list[User])
def get_users_r(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = get_users(db=db, skip=skip, limit=limit)
    return users

@router.get("/id:{user_id}", response_model=User)
def get_user_r(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/username:{username}", response_model=User)
def get_user_r(username: str, db: Session = Depends(get_db)):
    user = get_user_by_username(db=db, username=username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=User)
def update_user_r(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    return update_user(db=db, user_id=user_id, username=user.username, password=user.password)

@router.delete("/{user_id}", response_model=User)
def delete_user_r(user_id: int, db: Session = Depends(get_db)):
    return delete_user(db=db, user_id=user_id)