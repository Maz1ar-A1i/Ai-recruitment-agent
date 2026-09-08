"""Skill Gap Analyzer tool with severity classification."""
import logging
from app.schemas.job import JobRequirements
from app.schemas.evaluation import SkillMatchResult, SkillGapResult, SkillGapItem
from app.tools.skill_extractor import normalize_skill_name

logger = logging.getLogger(__name__)


def identify_skill_gaps(
    job_requirements: JobRequirements,
    match_result: SkillMatchResult
) -> SkillGapResult:
    """Agent tool: Determine skill gaps, assign severity (Critical, Moderate, Minor), and provide rationale."""
    gaps: list[SkillGapItem] = []
    req_set = {normalize_skill_name(s).lower() for s in job_requirements.required_skills}
    pref_set = {normalize_skill_name(s).lower() for s in job_requirements.preferred_skills}

    # Process missing skills
    for missing in match_result.missing_skills:
        missing_norm = normalize_skill_name(missing)
        missing_lower = missing_norm.lower()

        if missing_lower in req_set:
            gaps.append(SkillGapItem(
                skill=missing_norm,
                severity="Critical",
                rationale=f"Core required skill '{missing_norm}' is not documented in candidate profile; vital for primary responsibilities."
            ))
        elif missing_lower in pref_set:
            gaps.append(SkillGapItem(
                skill=missing_norm,
                severity="Minor",
                rationale=f"Preferred nice-to-have skill '{missing_norm}' is missing; can be picked up during standard onboarding."
            ))
        else:
            gaps.append(SkillGapItem(
                skill=missing_norm,
                severity="Moderate",
                rationale=f"Skill '{missing_norm}' is absent from candidate background, requiring additional ramp-up time."
            ))

    # Process partial matches
    for partial in match_result.partial_matches:
        base_skill = partial.split(" (via ")[0].strip()
        gaps.append(SkillGapItem(
            skill=base_skill,
            severity="Moderate",
            rationale=f"Candidate has adjacent experience ({partial}) but lacks demonstrated hands-on depth in the primary required tool."
        ))

    return SkillGapResult(gaps=gaps)
