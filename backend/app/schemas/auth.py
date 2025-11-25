# backend/app/schemas/auth.py
from datetime import datetime
from pydantic import BaseModel, EmailStr


# ---------- Shared user base ----------
class UserBase(BaseModel):
    email: EmailStr


# ---------- Signup request ----------
class UserCreate(UserBase):
    password: str  # plain password sent by frontend, will be hashed in service


# ---------- Login request ----------
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ---------- User info response ----------
class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# ---------- Token response (after login) ----------
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
