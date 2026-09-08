"""RecruiterDecision and RecruiterNote SQLAlchemy Models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class RecruiterDecision(Base):
    __tablename__ = "recruiter_decisions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    evaluation_id = Column(String(36), ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False)
    decision = Column(String(50), nullable=False)  # APPROVED, REJECTED, MODIFIED, PENDING
    modified_recommendation = Column(String(50), nullable=True)
    recruiter_notes = Column(Text, nullable=True)
    reviewer_name = Column(String(100), default="Recruiter")
    decided_at = Column(DateTime, default=datetime.utcnow)

    evaluation = relationship("Evaluation", back_populates="decisions")


class RecruiterNote(Base):
    __tablename__ = "recruiter_notes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = Column(String(36), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    author = Column(String(100), default="Recruiter")
    note = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
