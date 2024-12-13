from pydantic import BaseModel

class SatelliteBase(BaseModel):
    username: str
    is_active: bool = True
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: str

class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True