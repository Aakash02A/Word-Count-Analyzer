"""
SQLAlchemy model for User
"""
from sqlalchemy import Column, String, DateTime, Integer
from datetime import datetime
from backend.db.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(String, default="active")
    total_analyses = Column(Integer, default=0)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
