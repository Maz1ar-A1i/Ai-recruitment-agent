"""Report Generator tool for assembling comprehensive candidate evaluation."""
import logging
from app.llm.service import llm_service
from app.prompts.reporting import REPORT_SYSTEM_PROMPT, REPORT_USER_TEMPLATE
from app.schemas.job import JobRequirements
from app.schemas.candidate import CandidateProfile
from app.schemas.evaluation import (
    SkillMatchResult,
    SkillGapResult,
    ScoreBreakdown,
    InterviewQuestionsResult,
    CandidateReport,
)

logger = logging.getLogger(__name__)


def generate_candidate_report(
    job_requirements: JobRequirements,
    candidate_profile: CandidateProfile,
    match_result: SkillMatchResult,
    gap_result: SkillGapResult,
    score_breakdown: ScoreBreakdown,
    interview_result: InterviewQuestionsResult
) -> CandidateReport:
    """Agent tool: Synthesize all evaluation dimensions into a coherent CandidateReport."""
    strengths = []
    weaknesses = []
    concerns = []

    # Derive strengths deterministically from evidence and matches
    if match_result.matching_skills:
        strengths.append(f"Strong overlap in core required skills: {', '.join(match_result.matching_skills[:4])}.")
    if score_breakdown.experience_score >= 15:
        strengths.append(f"Solid relevant experience ({candidate_profile.years_of_experience} years) meeting role criteria.")
    if match_result.evidence_snippets:
        strengths.append("Verified hands-on evidence cited directly from past project and role achievements.")

    # Derive weaknesses & concerns
    for g in gap_result.gaps:
        if g.severity == "Critical":
            weaknesses.append(f"Critical deficiency in {g.skill}: {g.rationale}")
            concerns.append(f"Candidate lacks required production experience in {g.skill}.")
        elif g.severity == "Moderate":
            weaknesses.append(f"Moderate gap in {g.skill}: {g.rationale}")

    if not weaknesses:
        weaknesses.append("No major skill gaps identified against stated job requirements.")

    # Try LLM synthesis for natural prose, fallback to structured generation
    exp_analysis = (
        f"Candidate possesses {candidate_profile.years_of_experience} years of professional background. "
        f"Meets baseline experience threshold ({job_requirements.experience_required} years required)."
        if score_breakdown.experience_score >= 15
        else f"Candidate has {candidate_profile.years_of_experience} years against {job_requirements.experience_required} years requested."
    )

    edu_analysis = (
        f"Degree background aligns with role requirements ({job_requirements.education or 'Degree specified'})."
        if match_result.education_match
        else "Candidate possesses practical experience; degree field differs from specific requirement."
    )

    relevant_projects = [
        f"{p.name}: {p.description or 'Hands-on application'} (Technologies: {', '.join(p.technologies)})"
        for p in candidate_profile.projects
    ]

    ai_explanation = (
        f"{candidate_profile.name} achieved an overall match score of {score_breakdown.overall_score}/100, "
        f"earning a '{score_breakdown.recommendation}' recommendation. "
        f"Core technical competency scored {score_breakdown.skills_score}/50 with {len(match_result.matching_skills)} matching skills. "
        f"Identified {len(gap_result.gaps)} skill gaps across critical and moderate tiers."
    )

    return CandidateReport(
        candidate_name=candidate_profile.name,
        job_title=job_requirements.job_title,
        overall_score=score_breakdown.overall_score,
        recommendation=score_breakdown.recommendation,
        score_breakdown=score_breakdown,
        matching_skills=match_result.matching_skills,
        missing_skills=match_result.missing_skills,
        partial_matches=match_result.partial_matches,
        experience_analysis=exp_analysis,
        education_analysis=edu_analysis,
        relevant_projects=relevant_projects,
        strengths=strengths,
        weaknesses=weaknesses,
        skill_gaps=gap_result.gaps,
        potential_concerns=concerns,
        interview_questions=interview_result.questions,
        evidence_snippets=match_result.evidence_snippets,
        ai_explanation=ai_explanation
    )
