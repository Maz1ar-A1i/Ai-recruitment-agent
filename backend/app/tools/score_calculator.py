"""Deterministic Score Calculator tool."""
import logging
from app.config import settings
from app.schemas.job import JobRequirements
from app.schemas.candidate import CandidateProfile
from app.schemas.evaluation import SkillMatchResult, ScoreBreakdown
from app.tools.skill_extractor import normalize_skill_name

logger = logging.getLogger(__name__)


def calculate_candidate_score(
    job_requirements: JobRequirements,
    candidate_profile: CandidateProfile,
    match_result: SkillMatchResult
) -> ScoreBreakdown:
    """Agent tool: Compute transparent, deterministic mathematical score out of 100."""
    w_skills = settings.WEIGHT_SKILLS  # 0.50 -> 50 pts max
    w_exp = settings.WEIGHT_EXPERIENCE  # 0.20 -> 20 pts max
    w_edu = settings.WEIGHT_EDUCATION  # 0.10 -> 10 pts max
    w_pref = settings.WEIGHT_PREFERRED_SKILLS  # 0.10 -> 10 pts max
    w_proj = settings.WEIGHT_PROJECTS  # 0.10 -> 10 pts max

    # 1. Skills Match Score (0 to 50)
    req_skills = [normalize_skill_name(s).lower() for s in job_requirements.required_skills]
    matched_skills = [normalize_skill_name(s).lower() for s in match_result.matching_skills]
    partial_skills = match_result.partial_matches

    if req_skills:
        req_matched_count = sum(1 for r in req_skills if r in matched_skills)
        partial_count = len(partial_skills)
        # Full match gives 1.0, partial gives 0.5
        effective_matched = req_matched_count + (0.5 * partial_count)
        skills_ratio = min(effective_matched / len(req_skills), 1.0)
    else:
        skills_ratio = 1.0
    skills_score = round(skills_ratio * (w_skills * 100), 1)

    # 2. Experience Score (0 to 20)
    req_exp = job_requirements.experience_required or 0.0
    cand_exp = candidate_profile.years_of_experience or 0.0
    if req_exp > 0:
        exp_ratio = min(cand_exp / req_exp, 1.0)
    else:
        exp_ratio = 1.0 if cand_exp >= 0 else 0.5
    experience_score = round(exp_ratio * (w_exp * 100), 1)

    # 3. Education Score (0 to 10)
    if match_result.education_match:
        education_score = round(w_edu * 100, 1)
    elif candidate_profile.education:
        education_score = round((w_edu * 100) * 0.7, 1)  # has degree, different field
    else:
        education_score = round((w_edu * 100) * 0.4, 1)

    # 4. Preferred Skills Score (0 to 10)
    pref_skills = [normalize_skill_name(s).lower() for s in job_requirements.preferred_skills]
    if pref_skills:
        pref_matched_count = sum(1 for p in pref_skills if p in matched_skills)
        pref_ratio = min(pref_matched_count / len(pref_skills), 1.0)
    else:
        pref_ratio = 1.0
    preferred_skills_score = round(pref_ratio * (w_pref * 100), 1)

    # 5. Relevant Projects Score (0 to 10)
    # Check if candidate has projects that utilize matching or required skills
    if candidate_profile.projects:
        project_techs = []
        for p in candidate_profile.projects:
            project_techs.extend([t.lower() for t in p.technologies])
            if p.description:
                project_techs.extend([w.lower() for w in p.description.split()])
        
        has_overlap = any(s in " ".join(project_techs) for s in req_skills)
        if has_overlap:
            projects_score = round(w_proj * 100, 1)
        else:
            projects_score = round((w_proj * 100) * 0.6, 1)
    else:
        # If no explicit projects section, rely on work experience depth
        projects_score = round((w_proj * 100) * 0.5, 1)

    # Overall Score
    overall_score = round(
        skills_score + experience_score + education_score + preferred_skills_score + projects_score,
        1
    )
    overall_score = min(max(overall_score, 0.0), 100.0)

    # Determine Recommendation
    if overall_score >= settings.THRESHOLD_STRONG_MATCH:
        rec = "Strong Match"
    elif overall_score >= settings.THRESHOLD_MATCH:
        rec = "Match"
    elif overall_score >= settings.THRESHOLD_POTENTIAL_MATCH:
        rec = "Potential Match"
    else:
        rec = "Weak Match"

    return ScoreBreakdown(
        skills_score=skills_score,
        experience_score=experience_score,
        education_score=education_score,
        preferred_skills_score=preferred_skills_score,
        projects_score=projects_score,
        overall_score=overall_score,
        recommendation=rec,
        weights_applied={
            "skills": w_skills,
            "experience": w_exp,
            "education": w_edu,
            "preferred_skills": w_pref,
            "projects": w_proj,
        }
    )
