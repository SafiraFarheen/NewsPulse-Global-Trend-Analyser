from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class NewsBase(BaseModel):
    title: str
    source: str
    publishedAt: datetime
    url: str
    description: str | None = None

    class Config:
        orm_mode = True