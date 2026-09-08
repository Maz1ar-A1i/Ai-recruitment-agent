"""Unit tests for report validator and self-healing loop."""
import pytest
from app.tools.report_validator import validate_candidate_report
from app.schemas.job import JobRequirements
from app.schemas.candidate import CandidateProfile
from app.schemas.evaluation import CandidateReport, ScoreBreakdown, EvidenceSnippet


def test_validator_self_repairs_mismatched_score_and_recommendation():
    job = JobRequirements(
        job_title="Backend Engineer",
        required_skills=["Python"],
        experience_required=1.0
    )
    candidate = CandidateProfile(
        name="Alex Mercer",
        years_of_experience=2.0,
        skills=["Python"]
    )
    breakdown = ScoreBreakdown(
        skills_score=50.0,
        experience_score=20.0,
        education_score=10.0,
        preferred_skills_score=10.0,
        projects_score=5.0,
        overall_score=95.0,
        recommendation="Strong Match"
    )
    # Intentionally provide wrong overall_score (e.g. hallucinated 40.0 instead of 95.0)
    # and wrong recommendation "Weak Match"
    report = CandidateReport(
        candidate_name="Alex Mercer",
        job_title="Backend Engineer",
        overall_score=40.0,
        recommendation="Weak Match",
        score_breakdown=breakdown,
        experience_analysis="Good",
        education_analysis="Good",
        ai_explanation="Candidate achieved strong proficiency in core backend engineering.",
        evidence_snippets=[EvidenceSnippet(skill="Python", status="Strong Match", snippet="Wrote Python.")]
    )

    val_res = validate_candidate_report(report, job, candidate)
    assert val_res.repaired is True
    # Validator should fix overall_score to 95.0 and recommendation to "Strong Match"
    assert report.overall_score == 95.0
    assert report.recommendation == "Strong Match"
