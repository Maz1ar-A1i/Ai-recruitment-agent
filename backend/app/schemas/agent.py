"""Pydantic schemas for Agent Runs, Steps, and Execution Traces."""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class AgentStepSchema(BaseModel):
    id: str
    step_number: int
    tool_name: str
    thought: Optional[str] = None
    tool_input: Any = Field(default_factory=dict)
    tool_output: Any = Field(default_factory=dict)
    status: str
    execution_time_ms: float
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentRunResponse(BaseModel):
    id: str
    task: str
    job_id: Optional[str] = None
    candidate_id: Optional[str] = None
    evaluation_id: Optional[str] = None
    status: str
    total_steps: int
    duration_seconds: float
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    steps: list[AgentStepSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ToolInfo(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]


class AgentStatusResponse(BaseModel):
    status: str
    active_runs: int
    total_runs_completed: int
    registered_tools: list[str]
