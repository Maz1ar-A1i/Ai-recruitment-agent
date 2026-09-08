"""Recruitment Agent Orchestrator with execution loop and DB trace logging."""
import time
import uuid
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.agents.state import RecruitmentState
from app.agents.planner import planner
from app.agents.tool_registry import tool_registry
from app.models.agent import AgentRun, AgentStep
from app.models.evaluation import Evaluation, InterviewQuestion
from app.schemas.evaluation import CandidateReport

logger = logging.getLogger(__name__)


class RecruitmentAgent:
    """Agentic AI engine orchestrating the complete candidate evaluation workflow."""

    def __init__(self, db: Session):
        self.db = db

    def run(
        self,
        job_id: Optional[str] = None,
        candidate_id: Optional[str] = None,
        job_description: Optional[str] = None,
        resume_text: Optional[str] = None,
        task: str = "Evaluate candidate against job requirements"
    ) -> tuple[CandidateReport, str]:
        """Execute the agent loop until completion or maximum steps reached."""
        run_id = str(uuid.uuid4())
        start_time = time.time()

        # Initialize AgentRun record in database
        agent_run = AgentRun(
            id=run_id,
            task=task,
            job_id=job_id,
            candidate_id=candidate_id,
            status="RUNNING",
            started_at=datetime.utcnow()
        )
        self.db.add(agent_run)
        self.db.commit()

        # Initialize strongly typed state
        state = RecruitmentState(
            run_id=run_id,
            task=task,
            job_id=job_id,
            candidate_id=candidate_id,
            job_description=job_description,
            raw_resume_text=resume_text
        )

        step_counter = 0
        try:
            while not state.is_completed and step_counter < settings.MAX_AGENT_STEPS:
                step_counter += 1
                state.current_step = step_counter

                tool_name, tool_kwargs, thought = planner.determine_next_action(state)

                if tool_name == "complete_workflow":
                    logger.info("Agent decided workflow is complete at step %d", step_counter)
                    state.is_completed = True
                    break

                # Measure tool execution timing
                tool_start = time.time()
                try:
                    tool_output = tool_registry.execute_tool(tool_name, **tool_kwargs)
                    execution_time_ms = round((time.time() - tool_start) * 1000, 2)
                    step_status = "SUCCESS"
                except Exception as tool_err:
                    execution_time_ms = round((time.time() - tool_start) * 1000, 2)
                    step_status = "FAILED"
                    logger.error("Tool execution failed [%s]: %s", tool_name, tool_err)
                    tool_output = {"error": str(tool_err)}

                # Update typed state with tool output
                self._update_state_with_tool_output(state, tool_name, tool_output)

                # Persist AgentStep in DB
                agent_step = AgentStep(
                    agent_run_id=run_id,
                    step_number=step_counter,
                    tool_name=tool_name,
                    thought=thought,
                    tool_input=self._serialize_for_db(tool_kwargs),
                    tool_output=self._serialize_for_db(tool_output),
                    status=step_status,
                    execution_time_ms=execution_time_ms,
                    timestamp=datetime.utcnow()
                )
                self.db.add(agent_step)
                self.db.commit()

                if step_status == "FAILED":
                    # If critical tool failed, retry or break
                    state.error = f"Step {step_counter} ({tool_name}) failed: {tool_output.get('error')}"
                    break

            # Check loop exit condition
            if not state.candidate_report:
                raise RuntimeError(f"Agent failed to produce candidate report within {settings.MAX_AGENT_STEPS} steps.")

            # Save Evaluation to DB
            evaluation_id = str(uuid.uuid4())
            rep = state.candidate_report
            evaluation = Evaluation(
                id=evaluation_id,
                job_id=job_id or "adhoc_job",
                candidate_id=candidate_id or "adhoc_candidate",
                agent_run_id=run_id,
                overall_score=rep.overall_score,
                recommendation=rep.recommendation,
                skill_match_score=rep.score_breakdown.skills_score,
                experience_score=rep.score_breakdown.experience_score,
                education_score=rep.score_breakdown.education_score,
                preferred_skills_score=rep.score_breakdown.preferred_skills_score,
                projects_score=rep.score_breakdown.projects_score,
                matching_skills=rep.matching_skills,
                missing_skills=rep.missing_skills,
                partial_matches=rep.partial_matches,
                skill_gaps=[g.model_dump() for g in rep.skill_gaps],
                strengths=rep.strengths,
                weaknesses=rep.weaknesses,
                potential_concerns=rep.potential_concerns,
                evidence_snippets=[e.model_dump() for e in rep.evidence_snippets],
                ai_explanation=rep.ai_explanation
            )
            self.db.add(evaluation)

            # Save Interview Questions
            for q in rep.interview_questions:
                iq = InterviewQuestion(
                    evaluation_id=evaluation_id,
                    category=q.category,
                    question=q.question,
                    target_skill_or_gap=q.target_skill_or_gap,
                    rationale=q.rationale,
                    suggested_answer_points=q.suggested_answer_points
                )
                self.db.add(iq)

            # Update AgentRun record
            agent_run.status = "COMPLETED"
            agent_run.evaluation_id = evaluation_id
            agent_run.total_steps = step_counter
            agent_run.duration_seconds = round(time.time() - start_time, 2)
            agent_run.completed_at = datetime.utcnow()
            self.db.commit()

            return rep, run_id

        except Exception as e:
            logger.error("Agent execution loop failed: %s", e)
            agent_run.status = "FAILED"
            agent_run.error_message = str(e)
            agent_run.duration_seconds = round(time.time() - start_time, 2)
            agent_run.completed_at = datetime.utcnow()
            self.db.commit()
            raise

    def _update_state_with_tool_output(self, state: RecruitmentState, tool_name: str, output: any):
        if tool_name == "extract_job_requirements":
            state.job_requirements = output
        elif tool_name == "parse_resume":
            state.candidate_profile = output
            if not state.sanitized_resume_text and state.raw_resume_text:
                from app.tools.resume_parser import de_bias_resume_text
                state.sanitized_resume_text = de_bias_resume_text(state.raw_resume_text)
        elif tool_name == "extract_candidate_skills":
            state.candidate_skills = output
        elif tool_name == "match_candidate_to_job":
            state.skill_match = output
        elif tool_name == "identify_skill_gaps":
            state.skill_gaps = output
        elif tool_name == "calculate_candidate_score":
            state.score_breakdown = output
        elif tool_name == "generate_interview_questions":
            state.interview_result = output
        elif tool_name == "generate_candidate_report":
            state.candidate_report = output
        elif tool_name == "validate_candidate_report":
            state.validation_result = output

    def _serialize_for_db(self, obj: any) -> any:
        """Helper to serialize Pydantic models or dicts for JSON DB storage."""
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        elif isinstance(obj, dict):
            clean = {}
            for k, v in obj.items():
                if hasattr(v, "model_dump"):
                    clean[k] = v.model_dump()
                elif isinstance(v, (str, int, float, bool, list, dict)) or v is None:
                    clean[k] = v
                else:
                    clean[k] = str(v)
            return clean
        elif isinstance(obj, list):
            return [self._serialize_for_db(item) for item in obj]
        return str(obj)
