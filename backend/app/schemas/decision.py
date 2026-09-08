"""Pydantic schemas for Recruiter Decisions and Notes."""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class RecruiterDecisionCreate(BaseModel):
    evaluation_id: str
    decision: Literal["APPROVED", "REJECTED", "MODIFIED", "PENDING"]
    modified_recommendation: Optional[Literal["Strong Match", "Match", "Potential Match", "Weak Match"]] = None
    recruiter_notes: Optional[str] = Field(None, description="Recruiter rationale, interview observations, or adjustments")
    reviewer_name: Optional[str] = "Recruiter"


class RecruiterDecisionResponse(BaseModel):
    id: str
    evaluation_id: str
    decision: str
    modified_recommendation: Optional[str] = None
    recruiter_notes: Optional[str] = None
    reviewer_name: str
    decided_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecruiterNoteCreate(BaseModel):
    candidate_id: str
    author: Optional[str] = "Recruiter"
    note: str = Field(..., min_length=1)


class RecruiterNoteResponse(BaseModel):
    id: str
    candidate_id: str
    author: str
    note: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
