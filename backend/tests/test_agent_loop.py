"""Unit and integration tests for the Recruitment Agent loop and execution trace."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.agents.recruitment_agent import RecruitmentAgent
from app.models.agent import AgentRun, AgentStep
from app.models.evaluation import Evaluation


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_recruitment_agent_full_loop(in_memory_db):
    agent = RecruitmentAgent(in_memory_db)

    job_desc = """Job Title: Python Backend Engineer
Required Skills: Python, FastAPI, SQL
Preferred Skills: Docker, AWS
Experience: 2 years. Education: Bachelor's degree.
"""

    resume = """Candidate: Alex Mercer
Email: alex@example.com
2.5 years backend experience building APIs with Python and FastAPI.
Education: B.S. in Computer Science.
Skills: Python, FastAPI, SQL, Docker.
Projects: Built an inventory management system using FastAPI and PostgreSQL.
"""

    report, run_id = agent.run(
        job_description=job_desc,
        resume_text=resume,
        task="Evaluate candidate against job requirements"
    )

    assert report is not None
    assert report.overall_score > 0
    assert report.recommendation in ["Strong Match", "Match", "Potential Match", "Weak Match"]

    # Verify AgentRun in DB
    run_record = in_memory_db.query(AgentRun).filter(AgentRun.id == run_id).first()
    assert run_record is not None
    assert run_record.status == "COMPLETED"
    assert run_record.total_steps >= 8

    # Verify AgentSteps in DB
    steps = in_memory_db.query(AgentStep).filter(AgentStep.agent_run_id == run_id).order_by(AgentStep.step_number).all()
    assert len(steps) >= 8

    tool_names = [s.tool_name for s in steps]
    assert "extract_job_requirements" in tool_names
    assert "parse_resume" in tool_names
    assert "extract_candidate_skills" in tool_names
    assert "match_candidate_to_job" in tool_names
    assert "identify_skill_gaps" in tool_names
    assert "calculate_candidate_score" in tool_names
    assert "generate_interview_questions" in tool_names
    assert "generate_candidate_report" in tool_names
    assert "validate_candidate_report" in tool_names

    # Verify Evaluation in DB
    eval_record = in_memory_db.query(Evaluation).filter(Evaluation.agent_run_id == run_id).first()
    assert eval_record is not None
    assert eval_record.overall_score == report.overall_score
