"""Demo Mode and Dashboard Telemetry REST API endpoints."""
import uuid
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.job import Job
from app.models.candidate import Candidate
from app.models.evaluation import Evaluation
from app.models.agent import AgentRun, AgentStep
from app.models.knowledge import KnowledgeDocument, DocumentChunk
from app.agents.recruitment_agent import RecruitmentAgent
from app.rag.vector_store import rag_store
from app.rag.document_processor import chunk_text

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/demo", tags=["Demo & Telemetry"])

# Seed Data Constants
SAMPLE_JOB_TITLE = "Junior Python AI / Backend Engineer"
SAMPLE_JOB_DESC = """We are seeking a Junior Python AI / Backend Engineer to join our core intelligence team.
The engineer will build scalable REST APIs with FastAPI, integrate LLM pipelines, and maintain PostgreSQL data persistence.

Key Responsibilities:
- Design, test, and deploy RESTful microservices in Python using FastAPI.
- Integrate vector databases and embedding search with FAISS or pgvector.
- Write clean, well-tested Python code with PyTest and Git version control.
- Containerize services using Docker for cloud deployment.

Required Skills:
- Python 3.10+
- FastAPI or Flask
- REST APIs
- SQL / Relational Databases
- Git

Preferred Skills:
- Docker & Containerization
- AWS or Cloud Deployment
- LangChain / LLM Tool Calling
- PostgreSQL
- Redis

Experience & Education:
- 1+ years of practical software development or high-impact technical internships.
- Bachelor's degree in Computer Science, Software Engineering, or related STEM field.
"""

SAMPLE_CANDIDATE_ALICE = """Alice Chen
Email: alice.chen@example.com | Phone: +1 (555) 432-8765 | GitHub: github.com/alice-chen

PROFESSIONAL SUMMARY:
Proactive Junior Backend & AI Developer with 1.5 years experience building asynchronous RESTful APIs in Python using FastAPI, implementing Redis caching, and working with LangChain and vector embeddings. Passionate about agentic AI workflows and microservice architecture.

EXPERIENCE:
Junior Backend Engineer at Apex Innovations (June 2023 - Present)
- Developed 8+ production REST endpoints using Python and FastAPI for automated data ingestion.
- Optimized PostgreSQL queries and implemented Redis caching, cutting average endpoint latency by 28%.
- Utilized Git for feature branching, code reviews, and integrated CI/CD linting checks.
- Containerized local microservices using Docker and collaborated on staging deployments.

PROJECTS:
Agentic AI Task Orchestrator (2024)
- Built a multi-tool agentic AI prototype using FastAPI, LangChain, and FAISS for semantic document question-answering.
- Formulated custom Pydantic schemas for validated JSON tool calling.

EDUCATION:
B.S. in Computer Science, Pacific State University (Graduated May 2023, GPA 3.8/4.0)

TECHNICAL SKILLS:
Languages: Python, JavaScript, SQL
Frameworks: FastAPI, Flask, PyTorch, Scikit-Learn
Databases & Tools: PostgreSQL, Redis, Docker, Git, Linux
Cloud & AI: AWS (EC2, S3), LangChain, Vector Embeddings, FAISS
"""

SAMPLE_CANDIDATE_BOB = """Bob Miller
Email: bob.miller@example.com | Phone: +1 (555) 876-5432

SUMMARY:
Frontend-focused developer with 2 years of experience with React, TypeScript, and HTML/CSS. Recently learned basic Python scripting for web scraping.

EXPERIENCE:
Frontend Developer at WebCraft (2022 - Present)
- Created interactive dashboards using React and Tailwind CSS.
- Consumed backend REST APIs and handled state management.
- Wrote lightweight Python scripts to automate webpage scraping.

EDUCATION:
B.A. in Digital Arts, Metro College (2022)

SKILLS:
React, TypeScript, JavaScript, HTML5, CSS3, Basic Python, Git
"""

SAMPLE_CANDIDATE_CHARLIE = """Charlie Zhang
Email: charlie.z@example.com | Phone: +1 (555) 321-9876

SUMMARY:
Senior Data Engineer with 6 years of experience in Apache Spark, Scala, Hadoop, Kafka, and big data warehouse management.

EXPERIENCE:
Senior Big Data Engineer at DataStream Corp (2020 - Present)
- Architected enterprise batch and streaming pipelines processing 10TB+ daily.
- Deployed Spark clusters and managed Kafka queues.

EDUCATION:
M.S. in Computer Engineering (2018)

SKILLS:
Apache Spark, Scala, Kafka, Hadoop, Java, SQL, AWS, Kubernetes
"""

SAMPLE_POLICY = """ENGINEERING HIRING POLICY & GUIDELINES (2026)
1. Foundational Requirements:
For all Junior Engineering positions, verifiable coding proficiency in the primary team language (Python for Backend/AI) and understanding of REST design principles are non-negotiable prerequisites.

2. Cloud & Tooling Adaptability:
Candidates lacking direct AWS cloud experience may be hired if they demonstrate strong containerization concepts (Docker) and solid computer science fundamentals.

3. Fairness & Objective Evaluation:
Every applicant evaluation must be anchored strictly in verified code, work contributions, and demonstrated technical competence. Protected personal attributes must never influence candidate ranking.
"""


@router.post("/seed")
def seed_demo_data(db: Session = Depends(get_db)):
    """Seed sample jobs, candidates, and knowledge guidelines for instant exploration."""
    # 1. Seed Job
    job = db.query(Job).filter(Job.title == SAMPLE_JOB_TITLE).first()
    if not job:
        job = Job(
            id=str(uuid.uuid4()),
            title=SAMPLE_JOB_TITLE,
            description=SAMPLE_JOB_DESC,
            department="AI Engineering",
            location="San Francisco, CA (Hybrid)",
            experience_required=1.0,
            education_required="Bachelor's degree in Computer Science or STEM",
            required_skills=["Python", "FastAPI", "REST APIs", "SQL", "Git"],
            preferred_skills=["Docker", "AWS", "PostgreSQL", "Redis", "LangChain"],
            responsibilities=[
                "Design and deploy RESTful microservices in Python with FastAPI",
                "Integrate vector databases and embedding search",
                "Maintain test coverage with PyTest and Git CI/CD"
            ],
            soft_skills=["Clear communication", "Iterative problem solving"],
            keywords=["AI", "Backend", "FastAPI", "Python", "Microservices"]
        )
        db.add(job)
        db.commit()
        db.refresh(job)

    # 2. Seed Candidates
    candidates_data = [
        ("Alice Chen", SAMPLE_CANDIDATE_ALICE, 1.5, "alice_chen_resume.pdf"),
        ("Bob Miller", SAMPLE_CANDIDATE_BOB, 2.0, "bob_miller_resume.pdf"),
        ("Charlie Zhang", SAMPLE_CANDIDATE_CHARLIE, 6.0, "charlie_zhang_resume.pdf"),
    ]

    seeded_candidates = []
    for name, raw_text, exp, fname in candidates_data:
        cand = db.query(Candidate).filter(Candidate.name == name).first()
        if not cand:
            from app.tools.skill_extractor import normalize_skill_name
            skills_found = ["Python", "FastAPI", "PostgreSQL", "Docker", "Git", "Redis"] if "Alice" in name else (
                ["React", "TypeScript", "JavaScript", "Python", "Git"] if "Bob" in name else ["Apache Spark", "Scala", "Kafka", "SQL", "AWS"]
            )
            cand = Candidate(
                id=str(uuid.uuid4()),
                name=name,
                email=f"{name.lower().replace(' ', '.')}@example.com",
                phone="+1 (555) 012-3456",
                summary=f"Sample profile for {name}",
                years_of_experience=exp,
                education=[{"degree": "B.S. in Computer Science", "institution": "State University", "year": "2023"}],
                experience=[{"role": "Software Developer", "company": "Tech Innovations", "duration": "2022 - Present", "description": raw_text[:200]}],
                skills=skills_found,
                projects=[{"name": "Core Service Project", "description": "Hands-on application development", "technologies": skills_found[:3]}],
                certifications=[],
                raw_resume_text=raw_text,
                sanitized_resume_text=raw_text,
                file_name=fname
            )
            db.add(cand)
            db.commit()
            db.refresh(cand)
        seeded_candidates.append(cand)

    # 3. Seed Knowledge Doc
    kdoc = db.query(KnowledgeDocument).filter(KnowledgeDocument.title == "Engineering Hiring Policy & Guidelines").first()
    if not kdoc:
        doc_id = str(uuid.uuid4())
        chunks = chunk_text(SAMPLE_POLICY)
        kdoc = KnowledgeDocument(
            id=doc_id,
            title="Engineering Hiring Policy & Guidelines",
            filename="engineering_hiring_policy.txt",
            content=SAMPLE_POLICY,
            document_type="policy",
            chunks_count=len(chunks)
        )
        db.add(kdoc)
        for idx, c in enumerate(chunks):
            cid = str(uuid.uuid4())
            db.add(DocumentChunk(id=cid, document_id=doc_id, chunk_index=idx, content=c))
            rag_store.add_chunk(chunk_id=cid, document_title=kdoc.title, document_type=kdoc.document_type, content=c)
        db.commit()

    return {
        "message": "Sample jobs, candidates, and knowledge documents successfully seeded!",
        "job_id": job.id,
        "candidate_ids": [c.id for c in seeded_candidates]
    }


@router.post("/run")
def run_live_demo(db: Session = Depends(get_db)):
    """Execute end-to-end demo agent workflow for Alice Chen vs Junior Python AI Engineer."""
    # Ensure seed data exists
    seed_result = seed_demo_data(db)
    job_id = seed_result["job_id"]
    candidate_id = seed_result["candidate_ids"][0]  # Alice Chen

    job = db.query(Job).filter(Job.id == job_id).first()
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    agent = RecruitmentAgent(db)
    report, run_id = agent.run(
        job_id=job.id,
        candidate_id=candidate.id,
        job_description=job.description,
        resume_text=candidate.raw_resume_text,
        task=f"Demo: Evaluate {candidate.name} for {job.title}"
    )

    evaluation = db.query(Evaluation).filter(Evaluation.agent_run_id == run_id).first()
    agent_run = db.query(AgentRun).filter(AgentRun.id == run_id).first()

    return {
        "status": "COMPLETED",
        "demo_summary": {
            "candidate_name": candidate.name,
            "job_title": job.title,
            "overall_score": report.overall_score,
            "recommendation": report.recommendation,
            "total_steps": agent_run.total_steps if agent_run else 9,
            "duration_seconds": agent_run.duration_seconds if agent_run else 1.2
        },
        "evaluation_id": evaluation.id if evaluation else None,
        "agent_run_id": run_id,
        "report": report
    }


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get high-level statistics for executive dashboard."""
    total_jobs = db.query(Job).count()
    total_candidates = db.query(Candidate).count()
    total_evaluations = db.query(Evaluation).count()
    total_runs = db.query(AgentRun).count()

    avg_score = db.query(func.avg(Evaluation.overall_score)).scalar() or 0.0
    avg_score = round(float(avg_score), 1)

    strong_matches = db.query(Evaluation).filter(Evaluation.recommendation == "Strong Match").count()
    matches = db.query(Evaluation).filter(Evaluation.recommendation == "Match").count()
    potential_matches = db.query(Evaluation).filter(Evaluation.recommendation == "Potential Match").count()
    weak_matches = db.query(Evaluation).filter(Evaluation.recommendation == "Weak Match").count()

    recent_evaluations = db.query(Evaluation).order_by(Evaluation.created_at.desc()).limit(5).all()
    recent_runs = db.query(AgentRun).order_by(AgentRun.started_at.desc()).limit(5).all()

    return {
        "total_jobs": total_jobs,
        "total_candidates": total_candidates,
        "total_evaluations": total_evaluations,
        "total_agent_runs": total_runs,
        "average_score": avg_score,
        "distribution": {
            "strong_matches": strong_matches,
            "matches": matches,
            "potential_matches": potential_matches,
            "weak_matches": weak_matches
        },
        "recent_evaluations": [
            {
                "id": e.id,
                "job_id": e.job_id,
                "candidate_id": e.candidate_id,
                "score": e.overall_score,
                "recommendation": e.recommendation,
                "created_at": e.created_at
            }
            for e in recent_evaluations
        ],
        "recent_runs": [
            {
                "id": r.id,
                "task": r.task,
                "status": r.status,
                "total_steps": r.total_steps,
                "duration_seconds": r.duration_seconds,
                "started_at": r.started_at
            }
            for r in recent_runs
        ]
    }
