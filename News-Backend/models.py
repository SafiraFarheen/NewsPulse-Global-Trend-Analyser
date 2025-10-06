from sqlalchemy import Column, Integer, String, DateTime, Text
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

class NewsBase(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    source = Column(String)
    publishedAt = Column(DateTime, default=datetime.datetime.utcnow)
    url = Column(String, unique=True)
    description = Column(Text)
