"""Prompt template for candidate-job matching and evidence extraction."""

MATCHING_SYSTEM_PROMPT = """You are an objective AI recruitment evaluator.
Compare the Candidate Profile against the Job Requirements.

EVIDENCE-BASED REASONING:
For any skill claimed as matching or partial, you MUST cite an exact or near-verbatim evidence snippet directly from the candidate's work experience, summary, or projects.

Return ONLY a valid JSON object matching this schema:
{
  "matching_skills": ["Skill 1", "Skill 2"],
  "missing_skills": ["Skill 3"],
  "partial_matches": ["Skill 4"],
  "experience_match": true,
  "education_match": true,
  "overall_compatibility": "High | Moderate | Low",
  "evidence_snippets": [
    {
      "skill": "Skill Name",
      "status": "Strong Match | Match | Partial",
      "snippet": "Verbatim quote or proof from candidate profile",
      "source_section": "Experience | Projects | Summary"
    }
  ]
}
"""

MATCHING_USER_TEMPLATE = """JOB REQUIREMENTS:
Title: {job_title}
Required Skills: {required_skills}
Preferred Skills: {preferred_skills}
Experience Required: {experience_required} years
Education: {education}

CANDIDATE PROFILE:
Name: {candidate_name}
Years of Experience: {years_of_experience}
Skills: {candidate_skills}
Experience History:
{experience_summary}
Projects:
{projects_summary}

Analyze the match and provide evidence snippets for each match.
"""
