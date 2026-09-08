"""Candidate Matcher tool with evidence-based reasoning."""
import re
from typing import Optional
from app.schemas.job import JobRequirements
from app.schemas.candidate import CandidateProfile
from app.schemas.evaluation import SkillMatchResult, EvidenceSnippet
from app.tools.skill_extractor import normalize_skill_name

# Related technology affinities for partial matching
SKILL_AFFINITIES = {
    "FastAPI": ["Flask", "Django", "Tornado", "Express", "Node.js"],
    "Flask": ["FastAPI", "Django"],
    "Django": ["FastAPI", "Flask"],
    "PostgreSQL": ["MySQL", "SQL", "SQLite", "Oracle"],
    "MySQL": ["PostgreSQL", "SQL", "SQLite"],
    "Docker": ["Kubernetes", "Containerization", "Podman"],
    "Kubernetes": ["Docker", "ECS", "Nomad"],
    "AWS": ["GCP", "Azure", "Cloud"],
    "GCP": ["AWS", "Azure", "Cloud"],
    "Azure": ["AWS", "GCP", "Cloud"],
    "React": ["Vue", "Angular", "Next.js"],
    "PyTorch": ["TensorFlow", "Keras", "Scikit-Learn"],
    "TensorFlow": ["PyTorch", "Keras", "Scikit-Learn"],
}


def find_evidence_snippet(skill: str, candidate_profile: CandidateProfile, raw_text: Optional[str] = None) -> Optional[EvidenceSnippet]:
    """Search candidate profile sections and text for literal evidence sentences."""
    skill_lower = skill.lower()

    # Check work experience descriptions
    for exp in candidate_profile.experience:
        desc = exp.description or ""
        if skill_lower in desc.lower():
            for sentence in desc.split("."):
                if skill_lower in sentence.lower():
                    clean_sentence = sentence.strip() + "."
                    return EvidenceSnippet(
                        skill=skill,
                        status="Strong Match",
                        snippet=clean_sentence,
                        source_section=f"Experience at {exp.company or 'Company'}"
                    )

    # Check projects
    for proj in candidate_profile.projects:
        desc = proj.description or ""
        techs = [t.lower() for t in proj.technologies]
        if skill_lower in desc.lower() or skill_lower in techs:
            snippet = desc if desc else f"Used {skill} in {proj.name}."
            return EvidenceSnippet(
                skill=skill,
                status="Strong Match",
                snippet=snippet[:200],
                source_section=f"Project: {proj.name or 'Project'}"
            )

    # Check summary
    if candidate_profile.summary and skill_lower in candidate_profile.summary.lower():
        for sentence in candidate_profile.summary.split("."):
            if skill_lower in sentence.lower():
                return EvidenceSnippet(
                    skill=skill,
                    status="Match",
                    snippet=sentence.strip() + ".",
                    source_section="Professional Summary"
                )

    # Fallback to raw text
    if raw_text and skill_lower in raw_text.lower():
        for sentence in raw_text.split("."):
            if skill_lower in sentence.lower() and len(sentence.strip()) > 10:
                return EvidenceSnippet(
                    skill=skill,
                    status="Match",
                    snippet=sentence.strip() + ".",
                    source_section="Resume Text"
                )

    return None


def match_candidate_to_job(
    job_requirements: JobRequirements,
    candidate_profile: CandidateProfile,
    candidate_skills: Optional[list[str]] = None,
    raw_resume_text: Optional[str] = None
) -> SkillMatchResult:
    """Agent tool: Match candidate profile against job requirements with evidence citation."""
    # Normalize candidate skills
    c_skills = set(candidate_skills or [normalize_skill_name(s) for s in candidate_profile.skills])
    c_skills_lower = {s.lower(): s for s in c_skills}

    matching = set()
    missing = set()
    partial = set()
    evidence_list: list[EvidenceSnippet] = []

    # 1. Match Required Skills
    for req in job_requirements.required_skills:
        req_norm = normalize_skill_name(req)
        req_lower = req_norm.lower()

        if req_lower in c_skills_lower:
            matching.add(req_norm)
            ev = find_evidence_snippet(req_norm, candidate_profile, raw_resume_text)
            if ev:
                evidence_list.append(ev)
            else:
                evidence_list.append(EvidenceSnippet(
                    skill=req_norm,
                    status="Match",
                    snippet=f"Candidate lists verified competency in {req_norm}.",
                    source_section="Skills"
                ))
        else:
            # Check for partial matches / related technology
            affinities = SKILL_AFFINITIES.get(req_norm, [])
            found_affinity = False
            for aff in affinities:
                if aff.lower() in c_skills_lower:
                    partial.add(f"{req_norm} (via {aff})")
                    ev = find_evidence_snippet(aff, candidate_profile, raw_resume_text)
                    if ev:
                        ev.status = "Partial"
                        ev.skill = f"{req_norm} [Partial via {aff}]"
                        evidence_list.append(ev)
                    found_affinity = True
                    break
            if not found_affinity:
                missing.add(req_norm)

    # 2. Match Preferred Skills
    for pref in job_requirements.preferred_skills:
        pref_norm = normalize_skill_name(pref)
        if pref_norm.lower() in c_skills_lower:
            matching.add(pref_norm)
            ev = find_evidence_snippet(pref_norm, candidate_profile, raw_resume_text)
            if ev:
                evidence_list.append(ev)
            else:
                evidence_list.append(EvidenceSnippet(
                    skill=pref_norm,
                    status="Match",
                    snippet=f"Candidate lists preferred competency in {pref_norm}.",
                    source_section="Skills"
                ))

    # Experience Match
    exp_match = candidate_profile.years_of_experience >= (job_requirements.experience_required or 0.0)

    # Education Match
    edu_match = True
    if job_requirements.education:
        req_edu_lower = job_requirements.education.lower()
        has_degree = False
        for edu in candidate_profile.education:
            deg = (edu.degree or "").lower()
            field = (edu.field_of_study or "").lower()
            if "bachelor" in req_edu_lower and ("bachelor" in deg or "b.s." in deg or "b.e." in deg or "b.tech" in deg):
                has_degree = True
                break
            elif "master" in req_edu_lower and ("master" in deg or "m.s." in deg or "m.tech" in deg):
                has_degree = True
                break
            elif not req_edu_lower or req_edu_lower == "none":
                has_degree = True
                break
        edu_match = has_degree if candidate_profile.education else False

    # Overall compatibility category
    match_ratio = len(matching) / max(len(job_requirements.required_skills), 1)
    if match_ratio >= 0.8 and exp_match:
        compatibility = "High"
    elif match_ratio >= 0.5:
        compatibility = "Moderate"
    else:
        compatibility = "Low"

    return SkillMatchResult(
        matching_skills=sorted(list(matching)),
        missing_skills=sorted(list(missing)),
        partial_matches=sorted(list(partial)),
        experience_match=exp_match,
        education_match=edu_match,
        overall_compatibility=compatibility,
        evidence_snippets=evidence_list
    )
