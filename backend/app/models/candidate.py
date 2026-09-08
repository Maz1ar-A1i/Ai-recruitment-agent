"""Candidate SQLAlchemy Model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(100), nullable=True)
    summary = Column(Text, nullable=True)
    years_of_experience = Column(Float, default=0.0)
    education = Column(JSON, default=list)
    experience = Column(JSON, default=list)
    skills = Column(JSON, default=list)
    projects = Column(JSON, default=list)
    certifications = Column(JSON, default=list)
    raw_resume_text = Column(Text, nullable=False)
    sanitized_resume_text = Column(Text, nullable=True)
    file_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    evaluations = relationship("Evaluation", back_populates="candidate", cascade="all, delete-orphan")
