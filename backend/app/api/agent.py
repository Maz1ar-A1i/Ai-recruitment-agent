"""Agent Runs and Tool Registry REST API endpoints."""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.agent import AgentRun, AgentStep
from app.schemas.agent import AgentRunResponse, ToolInfo, AgentStatusResponse
from app.agents.tool_registry import tool_registry

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Agent"])


@router.get("/api/agent/runs", response_model=list[AgentRunResponse])
def list_agent_runs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List recent agent execution runs."""
    runs = db.query(AgentRun).order_by(AgentRun.started_at.desc()).offset(skip).limit(limit).all()
    return runs


@router.get("/api/agent/runs/{run_id}", response_model=AgentRunResponse)
def get_agent_run(run_id: str, db: Session = Depends(get_db)):
    """Retrieve details and full step-by-step trace of a specific agent run."""
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"AgentRun with ID '{run_id}' not found.")
    return run


@router.get("/api/agent/status", response_model=AgentStatusResponse)
def get_agent_status(db: Session = Depends(get_db)):
    """Get operational status and telemetry of the Recruitment Agent."""
    active_runs = db.query(AgentRun).filter(AgentRun.status == "RUNNING").count()
    total_completed = db.query(AgentRun).filter(AgentRun.status == "COMPLETED").count()
    tools = tool_registry.list_tools()

    return AgentStatusResponse(
        status="OPERATIONAL",
        active_runs=active_runs,
        total_runs_completed=total_completed,
        registered_tools=[t.name for t in tools]
    )


@router.get("/api/tools", response_model=list[ToolInfo])
def list_tools():
    """List all registered tools in the centralized ToolRegistry with descriptions and schemas."""
    return tool_registry.list_tools()
