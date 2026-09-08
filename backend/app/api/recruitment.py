"""Recruitment Evaluation and Human-in-the-Loop REST API endpoints."""
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.job import Job
from app.models.candidate import Candidate
from app.models.evaluation import Evaluation, InterviewQuestion
from app.models.decision import RecruiterDecision
from app.schemas.evaluation import (
    EvaluateCandidateRequest,
    EvaluationResponse,
    BatchEvaluateRequest,
    BatchEvaluateResponse,
    BatchEvaluateItem,
)
from app.schemas.decision import RecruiterDecisionCreate, RecruiterDecisionResponse
from app.agents.recruitment_agent import RecruitmentAgent

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/recruitment", tags=["Recruitment"])


@router.post("/evaluate", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
def evaluate_candidate(payload: EvaluateCandidateRequest, db: Session = Depends(get_db)):
    """Run full agentic workflow to evaluate candidate against job requirements."""
    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with ID '{payload.job_id}' not found.")

    candidate = db.query(Candidate).filter(Candidate.id == payload.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate with ID '{payload.candidate_id}' not found.")

    agent = RecruitmentAgent(db)
    try:
        report, run_id = agent.run(
            job_id=job.id,
            candidate_id=candidate.id,
            job_description=job.description,
            resume_text=candidate.raw_resume_text,
            task=f"Evaluate {candidate.name} for {job.title}"
        )
    except Exception as e:
        logger.error("Evaluation execution failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Recruitment agent workflow failed: {str(e)}")

    # Retrieve freshly created evaluation
    evaluation = db.query(Evaluation).filter(Evaluation.agent_run_id == run_id).first()
    if not evaluation:
        raise HTTPException(status_code=500, detail="Evaluation was not created successfully.")

    return evaluation


@router.post("/evaluate-batch", response_model=BatchEvaluateResponse)
def evaluate_candidates_batch(payload: BatchEvaluateRequest, db: Session = Depends(get_db)):
    """Batch evaluate multiple candidates against a job description with error resilience."""
    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with ID '{payload.job_id}' not found.")

    results: list[BatchEvaluateItem] = []
    successful = 0
    failed = 0

    agent = RecruitmentAgent(db)
    for cand_id in payload.candidate_ids:
        candidate = db.query(Candidate).filter(Candidate.id == cand_id).first()
        if not candidate:
            failed += 1
            results.append(BatchEvaluateItem(
                candidate_id=cand_id,
                candidate_name="Unknown",
                status="FAILED",
                error=f"Candidate with ID '{cand_id}' not found."
            ))
            continue

        try:
            report, run_id = agent.run(
                job_id=job.id,
                candidate_id=candidate.id,
                job_description=job.description,
                resume_text=candidate.raw_resume_text,
                task=f"Batch evaluate {candidate.name} for {job.title}"
            )
            eval_record = db.query(Evaluation).filter(Evaluation.agent_run_id == run_id).first()
            successful += 1
            results.append(BatchEvaluateItem(
                candidate_id=candidate.id,
                candidate_name=candidate.name,
                status="SUCCESS",
                evaluation_id=eval_record.id if eval_record else None,
                score=report.overall_score,
                recommendation=report.recommendation
            ))
        except Exception as e:
            logger.error("Error evaluating candidate %s: %s", candidate.id, e)
            failed += 1
            results.append(BatchEvaluateItem(
                candidate_id=candidate.id,
                candidate_name=candidate.name,
                status="FAILED",
                error=str(e)
            ))

    # Sort results by score descending
    results.sort(key=lambda x: x.score or 0.0, reverse=True)

    return BatchEvaluateResponse(
        job_id=job.id,
        total=len(payload.candidate_ids),
        successful=successful,
        failed=failed,
        results=results
    )


@router.get("/results/{evaluation_id}", response_model=EvaluationResponse)
def get_evaluation_result(evaluation_id: str, db: Session = Depends(get_db)):
    """Retrieve full evaluation report including questions and human decisions."""
    eval_record = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not eval_record:
        raise HTTPException(status_code=404, detail=f"Evaluation with ID '{evaluation_id}' not found.")
    return eval_record


@router.get("/job/{job_id}/evaluations", response_model=list[EvaluationResponse])
def list_job_evaluations(job_id: str, db: Session = Depends(get_db)):
    """Retrieve all candidate evaluations for a specific job, ranked by overall score."""
    evals = db.query(Evaluation).filter(Evaluation.job_id == job_id).order_by(Evaluation.overall_score.desc()).all()
    return evals


@router.post("/decide", response_model=RecruiterDecisionResponse, status_code=status.HTTP_201_CREATED)
def submit_recruiter_decision(payload: RecruiterDecisionCreate, db: Session = Depends(get_db)):
    """Submit human-in-the-loop recruiter decision (Approve, Reject, Modify) with recruiter notes."""
    eval_record = db.query(Evaluation).filter(Evaluation.id == payload.evaluation_id).first()
    if not eval_record:
        raise HTTPException(status_code=404, detail=f"Evaluation with ID '{payload.evaluation_id}' not found.")

    decision_id = str(uuid.uuid4())
    recruiter_decision = RecruiterDecision(
        id=decision_id,
        evaluation_id=payload.evaluation_id,
        decision=payload.decision,
        modified_recommendation=payload.modified_recommendation,
        recruiter_notes=payload.recruiter_notes,
        reviewer_name=payload.reviewer_name or "Recruiter"
    )
    db.add(recruiter_decision)
    db.commit()
    db.refresh(recruiter_decision)
    return recruiter_decision


@router.get("/decisions/{evaluation_id}", response_model=list[RecruiterDecisionResponse])
def get_recruiter_decisions(evaluation_id: str, db: Session = Depends(get_db)):
    """Retrieve recruiter decision history for an evaluation."""
    decisions = db.query(RecruiterDecision).filter(RecruiterDecision.evaluation_id == evaluation_id).order_by(RecruiterDecision.decided_at.desc()).all()
    return decisions
