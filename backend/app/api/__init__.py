"""API package."""
from app.api.jobs import router as jobs_router
from app.api.candidates import router as candidates_router
from app.api.recruitment import router as recruitment_router
from app.api.agent import router as agent_router
from app.api.knowledge import router as knowledge_router
from app.api.evaluation import router as evaluation_router
from app.api.demo import router as demo_router

__all__ = [
    "jobs_router",
    "candidates_router",
    "recruitment_router",
    "agent_router",
    "knowledge_router",
    "evaluation_router",
    "demo_router",
]
