"""Job Analyzer tool for extracting structured job requirements."""
import logging
from app.llm.service import llm_service
from app.prompts.job_analysis import JOB_ANALYSIS_SYSTEM_PROMPT, JOB_ANALYSIS_USER_TEMPLATE
from app.schemas.job import JobRequirements

logger = logging.getLogger(__name__)


def extract_job_requirements(job_description: str) -> JobRequirements:
    """Agent tool: Extract structured requirements from raw job description."""
    if not job_description or len(job_description.strip()) < 10:
        raise ValueError("Job description is too short or empty to analyze.")

    prompt = JOB_ANALYSIS_USER_TEMPLATE.format(job_description=job_description)

    requirements = llm_service.generate_structured(
        prompt=prompt,
        response_model=JobRequirements,
        system_prompt=JOB_ANALYSIS_SYSTEM_PROMPT
    )
    return requirements
