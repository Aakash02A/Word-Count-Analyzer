"""
SQLAlchemy model for Spark Jobs
"""
from sqlalchemy import Column, String, DateTime, JSON
from datetime import datetime
from backend.db.database import Base

class SparkJob(Base):
    __tablename__ = "spark_jobs"
    
    id = Column(String, primary_key=True, index=True)
    analysis_id = Column(String, index=True)
    job_id = Column(String, unique=True, index=True)
    status = Column(String)  # submitted, running, completed, failed
    metrics = Column(JSON)  # Job metrics
    logs = Column(String)  # Job logs
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
