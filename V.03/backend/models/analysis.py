"""
SQLAlchemy model for Analysis
"""
from sqlalchemy import Column, String, DateTime, Float, JSON, Text
from sqlalchemy.sql import func
from datetime import datetime
from backend.db.database import Base

class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(String, primary_key=True, index=True)
    input_type = Column(String)  # "file" or "url"
    input_metadata = Column(JSON)  # filename, url, size, etc
    status = Column(String, default="processing")  # processing, completed, failed
    raw_data = Column(Text)  # Raw extracted content
    processed_data = Column(JSON)  # Processed analysis results
    visualization_data = Column(JSON)  # Chart/viz data
    execution_time = Column(Float)  # Seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
