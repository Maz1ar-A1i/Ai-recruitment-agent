"""Skill Extractor and Normalizer with deterministic alias mapping."""
import re
from typing import Optional
from app.schemas.candidate import CandidateProfile

# Comprehensive canonical skill mapping
SKILL_ALIASES = {
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "py": "Python",
    "python": "Python",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "vue": "Vue",
    "vuejs": "Vue",
    "vue.js": "Vue",
    "angular": "Angular",
    "angularjs": "Angular",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "Google Cloud Platform",
    "azure": "Azure",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "rest": "REST APIs",
    "rest api": "REST APIs",
    "restful": "REST APIs",
    "restful api": "REST APIs",
    "restful apis": "REST APIs",
    "rest apis": "REST APIs",
    "graphql": "GraphQL",
    "git": "Git",
    "github": "Git",
    "gitlab": "Git",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "dl": "Deep Learning",
    "deep learning": "Deep Learning",
    "nlp": "Natural Language Processing",
    "natural language processing": "Natural Language Processing",
    "llm": "LLMs",
    "llms": "LLMs",
    "large language models": "LLMs",
    "genai": "Generative AI",
    "generative ai": "Generative AI",
    "rag": "RAG",
    "sql": "SQL",
    "nosql": "NoSQL",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "linux": "Linux",
    "bash": "Bash",
    "celery": "Celery",
    "kafka": "Kafka",
    "rabbitmq": "RabbitMQ",
}


def normalize_skill_name(skill: str) -> str:
    """Map any alias, abbreviation, or casing variation to canonical name."""
    clean = skill.strip()
    key = clean.lower()
    return SKILL_ALIASES.get(key, clean)


def extract_candidate_skills(candidate_profile: CandidateProfile, raw_text: Optional[str] = None) -> list[str]:
    """Agent tool: Extract and deterministically normalize candidate skills."""
    collected_skills = set()

    # From candidate_profile.skills
    for skill in candidate_profile.skills:
        canonical = normalize_skill_name(skill)
        collected_skills.add(canonical)

    # From candidate work experience skills_used
    for exp in candidate_profile.experience:
        for s in exp.skills_used:
            collected_skills.add(normalize_skill_name(s))

    # From candidate projects technologies
    for proj in candidate_profile.projects:
        for t in proj.technologies:
            collected_skills.add(normalize_skill_name(t))

    # If raw_text is provided, scan for any known canonical skills mentioned
    if raw_text:
        lower_raw = raw_text.lower()
        for alias, canonical in SKILL_ALIASES.items():
            pattern = rf"\b{re.escape(alias)}\b"
            if re.search(pattern, lower_raw):
                collected_skills.add(canonical)

    return sorted(list(collected_skills))
