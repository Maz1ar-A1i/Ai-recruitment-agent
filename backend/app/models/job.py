"""Job SQLAlchemy Model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    department = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    experience_required = Column(Float, default=0.0)
    education_required = Column(String(255), nullable=True)
    required_skills = Column(JSON, default=list)
    preferred_skills = Column(JSON, default=list)
    responsibilities = Column(JSON, default=list)
    soft_skills = Column(JSON, default=list)
    keywords = Column(JSON, default=list)
    raw_analysis = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    evaluations = relationship("Evaluation", back_populates="job", cascade="all, delete-orphan")
