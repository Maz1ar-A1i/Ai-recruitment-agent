"""OpenAI LLM Provider."""
import json
import logging
from typing import Type, TypeVar, Optional
import httpx
from pydantic import BaseModel
from app.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API implementation using direct REST endpoint."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAIProvider.")
        self.api_key = api_key
        self.model = model
        self.url = "https://api.openai.com/v1/chat/completions"

    def _call_api(self, messages: list, json_mode: bool = False) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        with httpx.Client(timeout=45.0) as client:
            resp = client.post(self.url, json=payload, headers=headers)
            if resp.status_code != 200:
                logger.error("OpenAI API error: %d - %s", resp.status_code, resp.text)
                resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return self._call_api(messages)

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
            + f"\nCRITICAL: Return strictly valid JSON adhering to this JSON Schema:\n{schema_json}"
        )
        messages = [
            {"role": "system", "content": enforced_sys_prompt},
            {"role": "user", "content": prompt}
        ]
        raw_text = self._call_api(messages, json_mode=True)
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
