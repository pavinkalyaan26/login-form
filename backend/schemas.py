from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserRead(BaseModel):
    id: str
    name: str
    email: str
    age: int | None = None
    gender: str | None = None
    address: str | None = None
    interests: str | None = None
    bio: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: str | None = None
    age: int | None = None
    gender: str | None = None
    address: str | None = None
    interests: str | None = None
    bio: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
