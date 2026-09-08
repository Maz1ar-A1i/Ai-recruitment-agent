"""Resume Parser tool with PDF/DOCX/TXT extraction and sensitive attribute de-biasing."""
import io
import re
import logging
from typing import Optional
import fitz  # PyMuPDF
import docx
from app.llm.service import llm_service
from app.prompts.resume_analysis import RESUME_ANALYSIS_SYSTEM_PROMPT, RESUME_ANALYSIS_USER_TEMPLATE
from app.schemas.candidate import CandidateProfile

logger = logging.getLogger(__name__)

# Patterns for sensitive/protected attributes to strip for bias mitigation
SENSITIVE_PATTERNS = [
    r"(?i)\b(gender|sex)\s*[:\-]?\s*(male|female|non-binary|other)\b",
    r"(?i)\b(marital\s*status)\s*[:\-]?\s*(single|married|divorced|widowed)\b",
    r"(?i)\b(religion|faith)\s*[:\-]?\s*[A-Za-z]+\b",
    r"(?i)\b(date\s*of\s*birth|dob)\s*[:\-]?\s*[\d\/\-\.]+\b",
    r"(?i)\b(nationality|citizenship)\s*[:\-]?\s*[A-Za-z]+\b",
    r"(?i)\b(ethnicity|race)\s*[:\-]?\s*[A-Za-z\s]+\b",
]


def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
    """Extract raw text from PDF, DOCX, or TXT file bytes."""
    lower_name = filename.lower()
    text = ""
    try:
        if lower_name.endswith(".pdf"):
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            pages_text = []
            for page in doc:
                pages_text.append(page.get_text())
            text = "\n".join(pages_text)
        elif lower_name.endswith(".docx"):
            doc = docx.Document(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            text = "\n".join(paragraphs)
        else:
            # Fallback text
            text = file_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        logger.error("Error reading file %s: %s", filename, e)
        raise ValueError(f"Could not extract text from {filename}: {e}")

    return text.strip()


def de_bias_resume_text(raw_text: str) -> str:
    """Remove sensitive personal attributes (gender, religion, marital status, etc.) for fairness."""
    sanitized = raw_text
    for pattern in SENSITIVE_PATTERNS:
        sanitized = re.sub(pattern, "[REDACTED_FOR_FAIRNESS]", sanitized)
    return sanitized


def parse_resume(resume_text: str) -> CandidateProfile:
    """Agent tool: Parse resume text into structured CandidateProfile using LLM."""
    if not resume_text or len(resume_text.strip()) < 10:
        raise ValueError("Resume text is too short or empty to parse.")

    sanitized_text = de_bias_resume_text(resume_text)
    prompt = RESUME_ANALYSIS_USER_TEMPLATE.format(resume_text=sanitized_text)

    profile = llm_service.generate_structured(
        prompt=prompt,
        response_model=CandidateProfile,
        system_prompt=RESUME_ANALYSIS_SYSTEM_PROMPT
    )
    return profile
