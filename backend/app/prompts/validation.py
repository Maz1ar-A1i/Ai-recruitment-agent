"""Prompt template for report validation and repair."""

VALIDATION_SYSTEM_PROMPT = """You are an AI Quality Assurance Officer verifying recruitment evaluation reports.
Your role is to inspect the candidate report against ground data and identify any:
1. Hallucinated skills or claims without backing evidence.
2. Inconsistencies between the computed score and the recommendation.
3. Unsupported claims in strengths or concerns.

Return ONLY a valid JSON object matching this schema:
{
  "is_valid": true,
  "issues": ["Issue description if any"],
  "repaired": false,
  "details": {
    "score_consistency": true,
    "evidence_alignment": true,
    "recommendation_alignment": true
  }
}
"""

VALIDATION_USER_TEMPLATE = """Verify this evaluation report:
Candidate Name: {candidate_name}
Target Role: {job_title}
Calculated Score: {overall_score}
Recommendation: {recommendation}

Report Content:
Strengths: {strengths}
Weaknesses: {weaknesses}
Gaps: {gaps}
Evidence Snippets: {evidence_snippets}

Check for validity, hallucination, and consistency.
"""
