"""Curated Ground Truth Evaluation Dataset for AI Quality Benchmarking."""

BENCHMARK_JOBS = [
    {
        "id": "job_bm_1",
        "title": "Senior Python Backend Engineer",
        "description": "Seeking a Senior Python Backend Engineer with at least 4 years of experience. Must have deep expertise in Python, FastAPI, PostgreSQL, and Docker. Experience with AWS and Redis is preferred. Bachelor's in CS required.",
        "expected_required": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        "expected_preferred": ["AWS", "Redis"],
        "expected_experience": 4.0
    },
    {
        "id": "job_bm_2",
        "title": "Junior AI / ML Engineer",
        "description": "Looking for an entry-level AI/ML Engineer with 1+ year experience in Python, PyTorch, Scikit-Learn, and Git. Knowledge of HuggingFace, RAG, or Vector Databases is nice to have.",
        "expected_required": ["Python", "PyTorch", "Scikit-Learn", "Git"],
        "expected_preferred": ["RAG", "HuggingFace"],
        "expected_experience": 1.0
    },
    {
        "id": "job_bm_3",
        "title": "Full Stack Engineer (React + Node)",
        "description": "Full Stack developer with 3+ years experience in JavaScript, TypeScript, React, and Node.js. Must know REST APIs and SQL. Docker is a plus.",
        "expected_required": ["JavaScript", "TypeScript", "React", "Node.js", "REST APIs", "SQL"],
        "expected_preferred": ["Docker"],
        "expected_experience": 3.0
    }
]

BENCHMARK_CANDIDATES = [
    {
        "id": "cand_bm_1",
        "name": "Jordan Lee",
        "resume_text": """
Jordan Lee
jordan.lee@example.com | +1 555-0199
Senior Backend Software Engineer with 5 years building scalable APIs and distributed systems.

EXPERIENCE:
Staff Backend Developer at CloudScale Inc (2021 - Present)
- Engineered asynchronous microservices in Python using FastAPI and PostgreSQL.
- Containerized applications using Docker and orchestrated deployments on AWS ECS.
- Designed Redis caching layers resulting in 40% latency reduction.

EDUCATION:
B.S. in Computer Science, University of California (2019)

SKILLS:
Python, FastAPI, PostgreSQL, Docker, AWS, Redis, Git, Linux
        """,
        "job_id": "job_bm_1",
        "expected_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS", "Redis", "Git", "Linux"],
        "expected_recommendation": "Strong Match"
    },
    {
        "id": "cand_bm_2",
        "name": "Morgan Taylor",
        "resume_text": """
Morgan Taylor
morgan.t@example.com
Junior Machine Learning Practitioner passionate about deep learning and computer vision.

EXPERIENCE:
AI Research Intern at DataLab (2023 - 2024, 1.2 years)
- Built predictive neural network models with Python and PyTorch.
- Trained classification pipelines using Scikit-Learn.
- Used Git for team model versioning.

EDUCATION:
B.S. in Data Science & Mathematics, Tech State University (2023)

SKILLS:
Python, PyTorch, Scikit-Learn, Git, Pandas, NumPy
        """,
        "job_id": "job_bm_2",
        "expected_skills": ["Python", "PyTorch", "Scikit-Learn", "Git", "Pandas", "NumPy"],
        "expected_recommendation": "Strong Match"
    },
    {
        "id": "cand_bm_3",
        "name": "Casey Rivera",
        "resume_text": """
Casey Rivera
casey.r@example.com
Entry level developer with basic Java and PHP experience. 6 months internship experience.

EXPERIENCE:
Junior Intern at WebStudio (6 months)
- Maintained legacy PHP scripts and basic HTML forms.
- Minor bug fixes with MySQL.

EDUCATION:
Associate Degree in General Studies (2024)

SKILLS:
PHP, MySQL, HTML, CSS, Java
        """,
        "job_id": "job_bm_1",
        "expected_skills": ["PHP", "MySQL", "HTML", "CSS", "Java"],
        "expected_recommendation": "Weak Match"
    }
]
