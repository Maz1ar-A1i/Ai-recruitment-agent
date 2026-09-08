"""Candidates REST API endpoints."""
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate, CandidateResponse, CandidateProfile
from app.tools.resume_parser import extract_text_from_bytes, parse_resume, de_bias_resume_text
from app.tools.skill_extractor import extract_candidate_skills

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/candidates", tags=["Candidates"])


@router.post("/upload", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def upload_candidate_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a candidate resume (PDF, DOCX, or TXT), parse profile with AI, and persist."""
    filename = file.filename or "resume.txt"
    file_bytes = await file.read()

    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds maximum size of 10MB.")

    # 1. Extract text from file bytes
    try:
        raw_text = extract_text_from_bytes(file_bytes, filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")

    if not raw_text or len(raw_text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Uploaded document contains insufficient or unreadable text.")

    # 2. De-bias text
    sanitized_text = de_bias_resume_text(raw_text)

    # 3. Parse resume with AI tool
    profile: CandidateProfile = parse_resume(raw_text)

    # 4. Extract & normalize skills
    normalized_skills = extract_candidate_skills(profile, raw_text)

    candidate_id = str(uuid.uuid4())
    candidate = Candidate(
        id=candidate_id,
        name=profile.name or "Candidate",
        email=profile.email,
        phone=profile.phone,
        summary=profile.summary,
        years_of_experience=profile.years_of_experience or 0.0,
        education=[e.model_dump() for e in profile.education],
        experience=[e.model_dump() for e in profile.experience],
        skills=normalized_skills,
        projects=[p.model_dump() for p in profile.projects],
        certifications=profile.certifications,
        raw_resume_text=raw_text,
        sanitized_resume_text=sanitized_text,
        file_name=filename
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.post("", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def create_candidate(payload: CandidateCreate, db: Session = Depends(get_db)):
    """Manually create a candidate profile."""
    candidate_id = str(uuid.uuid4())
    candidate = Candidate(
        id=candidate_id,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        summary=payload.summary,
        years_of_experience=payload.years_of_experience or 0.0,
        education=payload.education,
        experience=payload.experience,
        skills=payload.skills,
        projects=payload.projects,
        certifications=payload.certifications,
        raw_resume_text=payload.raw_resume_text,
        sanitized_resume_text=payload.sanitized_resume_text or de_bias_resume_text(payload.raw_resume_text),
        file_name=payload.file_name
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.get("", response_model=list[CandidateResponse])
def list_candidates(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all candidates."""
    candidates = db.query(Candidate).order_by(Candidate.created_at.desc()).offset(skip).limit(limit).all()
    return candidates


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: str, db: Session = Depends(get_db)):
    """Retrieve details for a specific candidate."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate with ID '{candidate_id}' not found.")
    return candidate


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidate(candidate_id: str, db: Session = Depends(get_db)):
    """Delete a candidate."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate with ID '{candidate_id}' not found.")
    db.delete(candidate)
    db.commit()
    return None
