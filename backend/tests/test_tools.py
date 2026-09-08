"""Unit tests for deterministic tools and de-biasing."""
import pytest
from app.tools.resume_parser import de_bias_resume_text
from app.tools.skill_extractor import normalize_skill_name, extract_candidate_skills
from app.tools.candidate_matcher import match_candidate_to_job
from app.tools.skill_gap_analyzer import identify_skill_gaps
from app.schemas.job import JobRequirements
from app.schemas.candidate import CandidateProfile, CandidateExperienceItem, CandidateProject


def test_de_bias_resume_text():
    raw = "Candidate: John Doe\nGender: Male\nMarital Status: Married\nReligion: Christianity\nDOB: 1990-05-12\nSkills: Python, SQL"
    sanitized = de_bias_resume_text(raw)
    assert "Male" not in sanitized
    assert "Married" not in sanitized
    assert "Christianity" not in sanitized
    assert "1990-05-12" not in sanitized
    assert "Python, SQL" in sanitized


def test_normalize_skill_name():
    assert normalize_skill_name("js") == "JavaScript"
    assert normalize_skill_name("Node") == "Node.js"
    assert normalize_skill_name("postgres") == "PostgreSQL"
    assert normalize_skill_name("ML") == "Machine Learning"
    assert normalize_skill_name("k8s") == "Kubernetes"
    assert normalize_skill_name("FastAPI") == "FastAPI"


def test_extract_candidate_skills():
    profile = CandidateProfile(
        name="Alex Mercer",
        skills=["python", "fastapi", "postgres"],
        experience=[
            CandidateExperienceItem(
                role="Developer",
                company="Corp",
                skills_used=["docker", "git"]
            )
        ],
        projects=[
            CandidateProject(
                name="App",
                technologies=["redis", "AWS"]
            )
        ]
    )
    extracted = extract_candidate_skills(profile, "Also worked with Node and ML in past roles.")
    assert "Python" in extracted
    assert "FastAPI" in extracted
    assert "PostgreSQL" in extracted
    assert "Docker" in extracted
    assert "Git" in extracted
    assert "Redis" in extracted
    assert "AWS" in extracted
    assert "Node.js" in extracted
    assert "Machine Learning" in extracted


def test_candidate_matching_and_gaps():
    job_reqs = JobRequirements(
        job_title="Python Backend Engineer",
        required_skills=["Python", "FastAPI", "SQL"],
        preferred_skills=["Docker", "AWS"],
        experience_required=2.0,
        education="Bachelor's degree"
    )

    candidate = CandidateProfile(
        name="Alex Mercer",
        years_of_experience=3.0,
        skills=["Python", "FastAPI", "PostgreSQL"],
        experience=[
            CandidateExperienceItem(
                role="Backend Dev",
                company="TechCorp",
                description="Engineered scalable APIs with Python and FastAPI. Optimized PostgreSQL queries."
            )
        ],
        projects=[]
    )

    match_res = match_candidate_to_job(job_reqs, candidate)
    assert "Python" in match_res.matching_skills
    assert "FastAPI" in match_res.matching_skills
    assert match_res.experience_match is True
    assert len(match_res.evidence_snippets) > 0

    gap_res = identify_skill_gaps(job_reqs, match_res)
    assert isinstance(gap_res.gaps, list)
