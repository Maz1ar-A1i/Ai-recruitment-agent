"""Main FastAPI application entry point for AI Recruitment Agent."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import init_db
from app.api import (
    jobs_router,
    candidates_router,
    recruitment_router,
    agent_router,
    knowledge_router,
    evaluation_router,
    demo_router,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context for startup initialization and graceful shutdown."""
    logger.info("Initializing database schemas...")
    init_db()
    logger.info("Database initialized successfully.")
    yield
    logger.info("Shutting down AI Recruitment Agent application.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Production-grade standalone AI Recruitment Agent orchestrating resume parsing, candidate evaluation, skill matching, and interview question generation.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for modern React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled Exception at %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please consult system logs for details."}
    )


# Health Check Endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint validating application and provider status."""
    return {
        "status": "HEALTHY",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "llm_provider": settings.LLM_PROVIDER,
        "database": "CONNECTED"
    }


# Include Routers
app.include_router(jobs_router)
app.include_router(candidates_router)
app.include_router(recruitment_router)
app.include_router(agent_router)
app.include_router(knowledge_router)
app.include_router(evaluation_router)
app.include_router(demo_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
