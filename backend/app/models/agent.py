"""AgentRun and AgentStep SQLAlchemy Models for execution traces."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task = Column(String(255), nullable=False)
    job_id = Column(String(36), nullable=True)
    candidate_id = Column(String(36), nullable=True)
    evaluation_id = Column(String(36), nullable=True)
    status = Column(String(50), default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED
    total_steps = Column(Integer, default=0)
    duration_seconds = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    steps = relationship("AgentStep", back_populates="agent_run", cascade="all, delete-orphan", order_by="AgentStep.step_number")


class AgentStep(Base):
    __tablename__ = "agent_steps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_run_id = Column(String(36), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False)
    step_number = Column(Integer, nullable=False)
    tool_name = Column(String(100), nullable=False)
    thought = Column(Text, nullable=True)
    tool_input = Column(JSON, default=dict)
    tool_output = Column(JSON, default=dict)
    status = Column(String(50), default="SUCCESS")  # SUCCESS, FAILED
    execution_time_ms = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)

    agent_run = relationship("AgentRun", back_populates="steps")
