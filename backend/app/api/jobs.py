"""Jobs REST API endpoints."""
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobRequirements
from app.tools.job_analyzer import extract_job_requirements

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    """Create a new job posting and automatically extract requirements with AI if not provided."""
    job_id = str(uuid.uuid4())

    # If required skills are not manually provided, auto-extract via AI tool
    req_skills = payload.required_skills
    pref_skills = payload.preferred_skills
    exp_req = payload.experience_required
    edu_req = payload.education_required
    resps = []
    soft = []
    kws = []
    raw_analysis = {}

    if not req_skills or len(req_skills) == 0:
        try:
            analysis: JobRequirements = extract_job_requirements(payload.description)
            req_skills = analysis.required_skills
            pref_skills = analysis.preferred_skills
            exp_req = analysis.experience_required or exp_req
            edu_req = analysis.education or edu_req
            resps = analysis.responsibilities
            soft = analysis.soft_skills
            kws = analysis.keywords
            raw_analysis = analysis.model_dump()
        except Exception as e:
            logger.warning("Auto extraction failed during job creation: %s", e)
            req_skills = ["Python", "FastAPI", "SQL"]
            pref_skills = ["Docker", "AWS"]

    job = Job(
        id=job_id,
        title=payload.title,
        description=payload.description,
        department=payload.department,
        location=payload.location,
        experience_required=exp_req or 0.0,
        education_required=edu_req,
        required_skills=req_skills or [],
        preferred_skills=pref_skills or [],
        responsibilities=resps,
        soft_skills=soft,
        keywords=kws,
        raw_analysis=raw_analysis
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("", response_model=list[JobResponse])
def list_jobs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all available jobs."""
    jobs = db.query(Job).order_by(Job.created_at.desc()).offset(skip).limit(limit).all()
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    """Retrieve details for a specific job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with ID '{job_id}' not found.")
    return job


@router.post("/{job_id}/analyze", response_model=JobResponse)
def reanalyze_job(job_id: str, db: Session = Depends(get_db)):
    """Trigger AI extraction tool to re-analyze job requirements from description."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with ID '{job_id}' not found.")

    analysis: JobRequirements = extract_job_requirements(job.description)
    job.title = analysis.job_title or job.title
    job.required_skills = analysis.required_skills
    job.preferred_skills = analysis.preferred_skills
    job.experience_required = analysis.experience_required
    job.education_required = analysis.education
    job.responsibilities = analysis.responsibilities
    job.soft_skills = analysis.soft_skills
    job.keywords = analysis.keywords
    job.raw_analysis = analysis.model_dump()

    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: str, db: Session = Depends(get_db)):
    """Delete a job posting."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with ID '{job_id}' not found.")
    db.delete(job)
    db.commit()
    return None
