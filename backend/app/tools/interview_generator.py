"""Interview Generator tool for personalized question formulation."""
import logging
from app.llm.service import llm_service
from app.prompts.interview import INTERVIEW_SYSTEM_PROMPT, INTERVIEW_USER_TEMPLATE
from app.schemas.job import JobRequirements
from app.schemas.candidate import CandidateProfile
from app.schemas.evaluation import SkillMatchResult, SkillGapResult, InterviewQuestionsResult, InterviewQuestionItem

logger = logging.getLogger(__name__)


def generate_interview_questions(
    job_requirements: JobRequirements,
    candidate_profile: CandidateProfile,
    match_result: SkillMatchResult,
    gap_result: SkillGapResult
) -> InterviewQuestionsResult:
    """Agent tool: Generate role- and candidate-tailored interview questions."""
    exp_overview = "; ".join([
        f"{e.role} at {e.company} ({e.duration}): {e.description}"
        for e in candidate_profile.experience[:2]
    ]) or "Standard engineering experience"

    proj_overview = "; ".join([
        f"{p.name} ({', '.join(p.technologies)}): {p.description}"
        for p in candidate_profile.projects[:2]
    ]) or "Standard project portfolio"

    gaps_str = ", ".join([f"{g.skill} ({g.severity})" for g in gap_result.gaps]) or "None detected"

    prompt = INTERVIEW_USER_TEMPLATE.format(
        job_title=job_requirements.job_title,
        required_skills=", ".join(job_requirements.required_skills),
        candidate_name=candidate_profile.name,
        experience_overview=exp_overview,
        projects_overview=proj_overview,
        skill_gaps=gaps_str
    )

    try:
        result = llm_service.generate_structured(
            prompt=prompt,
            response_model=InterviewQuestionsResult,
            system_prompt=INTERVIEW_SYSTEM_PROMPT
        )
        if result.questions:
            return result
    except Exception as e:
        logger.warning("LLM interview generation encountered exception: %s. Using deterministic fallback.", e)

    # Deterministic fallback question set tailored to candidate profile
    fallback_questions: list[InterviewQuestionItem] = []

    # 1. Technical question based on top matched skill
    top_skill = match_result.matching_skills[0] if match_result.matching_skills else "Python"
    fallback_questions.append(InterviewQuestionItem(
        category="Technical",
        question=f"Can you explain your approach to architecting scalable services with {top_skill} and how you handle concurrent requests?",
        target_skill_or_gap=top_skill,
        rationale=f"Evaluates depth of practical design experience in {top_skill}.",
        suggested_answer_points=[
            "Explains concurrency models, thread pools, or async event loops",
            "Mentions monitoring, profiling, and bottleneck mitigation"
        ]
    ))

    # 2. Project-based question based on candidate's project
    if candidate_profile.projects:
        p = candidate_profile.projects[0]
        fallback_questions.append(InterviewQuestionItem(
            category="Project-based",
            question=f"In your project '{p.name}', what were the key architectural trade-offs you made, and how did you validate performance?",
            target_skill_or_gap=p.name or "System Design",
            rationale="Verifies authentic hands-on ownership and design rationale.",
            suggested_answer_points=[
                "Articulates design constraints and why specific technologies were chosen",
                "Shares concrete metrics or test outcomes"
            ]
        ))

    # 3. Skill-gap question based on identified gap
    if gap_result.gaps:
        gap = gap_result.gaps[0]
        fallback_questions.append(InterviewQuestionItem(
            category="Skill-gap",
            question=f"We noticed you have limited direct experience with {gap.skill}. How would you approach quickly onboarding and contributing to our codebase in this area?",
            target_skill_or_gap=gap.skill,
            rationale=f"Assesses candidate adaptability and learning curve for {gap.skill}.",
            suggested_answer_points=[
                "Cites past examples of quickly mastering new frameworks or tools",
                "Demonstrates solid conceptual foundation"
            ]
        ))

    # 4. Behavioral question
    fallback_questions.append(InterviewQuestionItem(
        category="Behavioral",
        question="Tell us about a technical disagreement you had with a teammate or reviewer on an API contract. How did you resolve it?",
        target_skill_or_gap="Team Collaboration",
        rationale="Evaluates professional communication, constructive debate, and emotional intelligence.",
        suggested_answer_points=[
            "Focuses on data, benchmarks, or user requirements rather than ego",
            "Maintains productive and respectful working relationships"
        ]
    ))

    return InterviewQuestionsResult(questions=fallback_questions)
