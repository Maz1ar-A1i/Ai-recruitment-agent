"""Report Validator tool for enforcing score consistency and integrity."""
import logging
from app.config import settings
from app.schemas.job import JobRequirements
from app.schemas.candidate import CandidateProfile
from app.schemas.evaluation import CandidateReport, ValidationResult

logger = logging.getLogger(__name__)


def validate_candidate_report(
    report: CandidateReport,
    job_requirements: JobRequirements,
    candidate_profile: CandidateProfile
) -> ValidationResult:
    """Agent tool: Validate candidate report against integrity rules, scores, and evidence."""
    issues: list[str] = []
    repaired = False

    # 1. Score range check
    if report.overall_score < 0.0 or report.overall_score > 100.0:
        issues.append(f"Invalid overall_score: {report.overall_score} is outside [0, 100].")

    # 2. Score breakdown summation check
    sb = report.score_breakdown
    computed_sum = round(
        sb.skills_score + sb.experience_score + sb.education_score + sb.preferred_skills_score + sb.projects_score,
        1
    )
    if abs(report.overall_score - computed_sum) > 0.5:
        issues.append(f"Score mismatch: overall_score ({report.overall_score}) does not match breakdown sum ({computed_sum}).")
        report.overall_score = computed_sum
        repaired = True

    # 3. Recommendation consistency check
    expected_rec = "Weak Match"
    if report.overall_score >= settings.THRESHOLD_STRONG_MATCH:
        expected_rec = "Strong Match"
    elif report.overall_score >= settings.THRESHOLD_MATCH:
        expected_rec = "Match"
    elif report.overall_score >= settings.THRESHOLD_POTENTIAL_MATCH:
        expected_rec = "Potential Match"

    if report.recommendation != expected_rec:
        issues.append(f"Recommendation mismatch: report says '{report.recommendation}' but score {report.overall_score} dictates '{expected_rec}'.")
        report.recommendation = expected_rec
        report.score_breakdown.recommendation = expected_rec
        repaired = True

    # 4. Evidence alignment check
    for ev in report.evidence_snippets:
        if not ev.snippet or len(ev.snippet.strip()) < 5:
            issues.append(f"Empty evidence snippet found for skill '{ev.skill}'.")

    # 5. Candidate name alignment
    if report.candidate_name.lower().strip() != candidate_profile.name.lower().strip():
        issues.append(f"Candidate name mismatch: '{report.candidate_name}' vs '{candidate_profile.name}'.")
        report.candidate_name = candidate_profile.name
        repaired = True

    is_valid = len(issues) == 0 or repaired

    return ValidationResult(
        is_valid=is_valid,
        issues=issues,
        repaired=repaired,
        details={
            "score_consistency": abs(report.overall_score - computed_sum) <= 0.5,
            "recommendation_alignment": report.recommendation == expected_rec,
            "evidence_count": len(report.evidence_snippets),
            "issues_count": len(issues),
        }
    )
