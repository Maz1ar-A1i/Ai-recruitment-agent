"""Agent Planner: determines next tool execution based on state analysis."""
import logging
from typing import Tuple, Any, Dict
from app.agents.state import RecruitmentState

logger = logging.getLogger(__name__)


class RecruitmentPlanner:
    """Planner that reasons over RecruitmentState and selects the optimal next tool."""

    def determine_next_action(self, state: RecruitmentState) -> Tuple[str, dict[str, Any], str]:
        """Returns (tool_name, tool_kwargs, thought)."""
        # Step 1: Job requirements extraction
        if not state.job_requirements:
            thought = "Job requirements have not been analyzed yet. Invoking extract_job_requirements tool to determine role expectations."
            return (
                "extract_job_requirements",
                {"job_description": state.job_description or ""},
                thought
            )

        # Step 2: Resume parsing
        if not state.candidate_profile:
            thought = "Candidate resume has not been parsed. Invoking parse_resume with de-biasing to extract structured candidate profile."
            return (
                "parse_resume",
                {"resume_text": state.raw_resume_text or ""},
                thought
            )

        # Step 3: Skill extraction & normalization
        if not state.candidate_skills:
            thought = "Candidate profile is available. Invoking extract_candidate_skills to normalize skill aliases and extract verified competencies."
            return (
                "extract_candidate_skills",
                {"candidate_profile": state.candidate_profile, "raw_text": state.raw_resume_text},
                thought
            )

        # Step 4: Candidate-job matching
        if not state.skill_match:
            thought = "Requirements and candidate skills are ready. Invoking match_candidate_to_job to evaluate skill alignment and extract evidence snippets."
            return (
                "match_candidate_to_job",
                {
                    "job_requirements": state.job_requirements,
                    "candidate_profile": state.candidate_profile,
                    "candidate_skills": state.candidate_skills,
                    "raw_resume_text": state.raw_resume_text
                },
                thought
            )

        # Step 5: Skill gaps identification
        if not state.skill_gaps:
            thought = "Skill match evaluated. Invoking identify_skill_gaps to categorize missing and partial skills into Critical, Moderate, and Minor tiers."
            return (
                "identify_skill_gaps",
                {
                    "job_requirements": state.job_requirements,
                    "match_result": state.skill_match
                },
                thought
            )

        # Step 6: Transparent score calculation
        if not state.score_breakdown:
            thought = "Skill match and gaps are established. Invoking calculate_candidate_score to compute a transparent, deterministic score out of 100."
            return (
                "calculate_candidate_score",
                {
                    "job_requirements": state.job_requirements,
                    "candidate_profile": state.candidate_profile,
                    "match_result": state.skill_match
                },
                thought
            )

        # Step 7: Personalized interview question generation
        if not state.interview_result:
            thought = "Scores computed. Invoking generate_interview_questions to formulate personalized Technical, Project, Gap, and Behavioral interview questions."
            return (
                "generate_interview_questions",
                {
                    "job_requirements": state.job_requirements,
                    "candidate_profile": state.candidate_profile,
                    "match_result": state.skill_match,
                    "gap_result": state.skill_gaps
                },
                thought
            )

        # Step 8: Comprehensive report generation
        if not state.candidate_report:
            thought = "All intermediate data ready. Invoking generate_candidate_report to synthesize findings into a structured executive report."
            return (
                "generate_candidate_report",
                {
                    "job_requirements": state.job_requirements,
                    "candidate_profile": state.candidate_profile,
                    "match_result": state.skill_match,
                    "gap_result": state.skill_gaps,
                    "score_breakdown": state.score_breakdown,
                    "interview_result": state.interview_result
                },
                thought
            )

        # Step 9: Report validation
        if not state.validation_result:
            thought = "Candidate report generated. Invoking validate_candidate_report to enforce mathematical score integrity and verify evidence backing."
            return (
                "validate_candidate_report",
                {
                    "report": state.candidate_report,
                    "job_requirements": state.job_requirements,
                    "candidate_profile": state.candidate_profile
                },
                thought
            )

        # Self-correction check: if validation discovered issues and repaired them, or if valid
        if state.validation_result.is_valid:
            thought = "Report has been successfully validated with no critical integrity violations. Concluding agent workflow."
            return ("complete_workflow", {}, thought)
        else:
            # Self-healing loop: re-run report generator with fixed scores
            thought = f"Validation flagged issues ({', '.join(state.validation_result.issues)}). Re-synthesizing report to repair discrepancies."
            return (
                "generate_candidate_report",
                {
                    "job_requirements": state.job_requirements,
                    "candidate_profile": state.candidate_profile,
                    "match_result": state.skill_match,
                    "gap_result": state.skill_gaps,
                    "score_breakdown": state.score_breakdown,
                    "interview_result": state.interview_result
                },
                thought
            )


planner = RecruitmentPlanner()
