"""Google Gemini LLM Provider."""
import json
import logging
from typing import Type, TypeVar, Optional
import httpx
from pydantic import BaseModel
from app.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API implementation using direct REST endpoint."""

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required for GeminiProvider.")
        self.api_key = api_key
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def _call_api(self, contents: list, system_instruction: Optional[str] = None, response_mime_type: Optional[str] = None) -> str:
        url = f"{self.base_url}?key={self.api_key}"
        payload = {"contents": contents}
        if system_instruction:
            payload["system_instruction"] = {
                "parts": [{"text": system_instruction}]
            }
        generation_config = {}
        if response_mime_type:
            generation_config["response_mime_type"] = response_mime_type
        if generation_config:
            payload["generationConfig"] = generation_config

        with httpx.Client(timeout=45.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code != 200:
                logger.error("Gemini API error: %d - %s", resp.status_code, resp.text)
                resp.raise_for_status()
            data = resp.json()
            try:
                candidate = data["candidates"][0]
                text = candidate["content"]["parts"][0]["text"]
                return text.strip()
            except (KeyError, IndexError) as e:
                raise ValueError(f"Malformed response from Gemini: {data}") from e

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        return self._call_api(contents, system_instruction=system_prompt)

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> T:
        schema_json = json.dumps(response_model.model_json_schema())
        enforced_sys_prompt = (
            (system_prompt or "")
            + f"\nCRITICAL: Return strictly valid JSON adhering to this JSON Schema:\n{schema_json}\nDo not include code markdown ticks or explanatory text."
        )
        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        raw_text = self._call_api(contents, system_instruction=enforced_sys_prompt, response_mime_type="application/json")
        
        # Clean potential markdown ticks if returned
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        parsed = json.loads(cleaned)
        return response_model.model_validate(parsed)
