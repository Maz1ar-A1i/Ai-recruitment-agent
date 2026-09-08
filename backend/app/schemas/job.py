"""Pydantic schemas for Job and Requirements."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class JobRequirements(BaseModel):
    """Structured extraction from a job description."""
    job_title: str = Field(..., description="Normalized job title")
    required_skills: list[str] = Field(default_factory=list, description="Must-have technical or domain skills")
    preferred_skills: list[str] = Field(default_factory=list, description="Nice-to-have skills or technologies")
    experience_required: float = Field(0.0, description="Minimum required years of experience")
    education: Optional[str] = Field(None, description="Required education level or field")
    responsibilities: list[str] = Field(default_factory=list, description="Core day-to-day responsibilities")
    technical_requirements: list[str] = Field(default_factory=list, description="Specific tech stack or architecture items")
    soft_skills: list[str] = Field(default_factory=list, description="Communication, teamwork, leadership, etc.")
    keywords: list[str] = Field(default_factory=list, description="Domain keywords and industry terms")


class JobCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: str = Field(..., min_length=10)
    department: Optional[str] = None
    location: Optional[str] = None
    experience_required: Optional[float] = 0.0
    education_required: Optional[str] = None
    required_skills: Optional[list[str]] = None
    preferred_skills: Optional[list[str]] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    experience_required: Optional[float] = None
    education_required: Optional[str] = None
    required_skills: Optional[list[str]] = None
    preferred_skills: Optional[list[str]] = None


class JobResponse(BaseModel):
    id: str
    title: str
    description: str
    department: Optional[str] = None
    location: Optional[str] = None
    experience_required: float
    education_required: Optional[str] = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
