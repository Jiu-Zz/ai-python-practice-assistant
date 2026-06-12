from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRead(BaseModel):
    id: int
    username: str
    email: str
    nickname: Optional[str] = None
    role: str
    learning_stage: str

    class Config:
        from_attributes = True


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    learning_stage: str = "basic"
    nickname: Optional[str] = None


class LoginRequest(BaseModel):
    account: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user: UserRead


class ProfileUpdate(BaseModel):
    learning_stage: Optional[str] = None
    nickname: Optional[str] = Field(default=None, max_length=64)
