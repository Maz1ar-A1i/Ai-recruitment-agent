"""Unit tests for transparent deterministic score calculation."""
import pytest
from app.tools.score_calculator import calculate_candidate_score
from app.schemas.job import JobRequirements
from app.schemas.candidate import CandidateProfile, CandidateProject
from app.schemas.evaluation import SkillMatchResult


def test_calculate_score_strong_match():
    job = JobRequirements(
        job_title="Senior Python Engineer",
        required_skills=["Python", "FastAPI", "SQL"],
        preferred_skills=["Docker"],
        experience_required=3.0,
        education="Bachelor's in CS"
    )

    candidate = CandidateProfile(
        name="Alice",
        years_of_experience=4.0,
        skills=["Python", "FastAPI", "SQL", "Docker"],
        education=[{"degree": "B.S. in CS", "institution": "State Univ"}],
        projects=[CandidateProject(name="API Service", technologies=["Python", "FastAPI"])]
    )

    match = SkillMatchResult(
        matching_skills=["Python", "FastAPI", "SQL", "Docker"],
        missing_skills=[],
        partial_matches=[],
        experience_match=True,
        education_match=True
    )

    score_res = calculate_candidate_score(job, candidate, match)
    assert score_res.overall_score >= 85.0
    assert score_res.recommendation == "Strong Match"
    assert score_res.skills_score == 50.0
    assert score_res.experience_score == 20.0
    assert score_res.education_score == 10.0


def test_calculate_score_weak_match():
    job = JobRequirements(
        job_title="Python Engineer",
        required_skills=["Python", "FastAPI", "SQL", "Docker", "AWS"],
        preferred_skills=["Kubernetes"],
        experience_required=5.0
    )

    candidate = CandidateProfile(
        name="Bob",
        years_of_experience=0.5,
        skills=["HTML", "CSS"],
        education=[],
        projects=[]
    )

    match = SkillMatchResult(
        matching_skills=[],
        missing_skills=["Python", "FastAPI", "SQL", "Docker", "AWS"],
        partial_matches=[],
        experience_match=False,
        education_match=False
    )

    score_res = calculate_candidate_score(job, candidate, match)
    assert score_res.overall_score < 50.0
    assert score_res.recommendation == "Weak Match"
    assert score_res.skills_score == 0.0
