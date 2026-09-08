"""Pydantic schemas for Candidate profiles and parsing."""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class CandidateEducation(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[str] = None
    field_of_study: Optional[str] = None


class CandidateExperienceItem(BaseModel):
    role: Optional[str] = None
    company: Optional[str] = None
    duration: Optional[str] = None
    years: Optional[float] = 0.0
    description: Optional[str] = None
    skills_used: list[str] = Field(default_factory=list)


class CandidateProject(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: list[str] = Field(default_factory=list)
    link: Optional[str] = None


class CandidateProfile(BaseModel):
    """Structured candidate profile extracted from resume."""
    name: str = Field(..., description="Candidate full name")
    email: Optional[str] = Field(None, description="Candidate email address")
    phone: Optional[str] = Field(None, description="Candidate contact number")
    summary: Optional[str] = Field(None, description="Professional summary or bio")
    education: list[CandidateEducation] = Field(default_factory=list)
    experience: list[CandidateExperienceItem] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list, description="Extracted and normalized skills")
    projects: list[CandidateProject] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    years_of_experience: float = Field(0.0, description="Calculated or stated total years of experience")


class CandidateCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    summary: Optional[str] = None
    years_of_experience: Optional[float] = 0.0
    education: list[dict[str, Any]] = Field(default_factory=list)
    experience: list[dict[str, Any]] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[dict[str, Any]] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    raw_resume_text: str
    sanitized_resume_text: Optional[str] = None
    file_name: Optional[str] = None


class CandidateResponse(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    summary: Optional[str] = None
    years_of_experience: float
    education: list[Any] = Field(default_factory=list)
    experience: list[Any] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[Any] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    file_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
