"""LLM Service orchestrator with retry logic, backoff, and fallback handling."""
import time
import logging
from typing import Type, TypeVar, Optional
from pydantic import BaseModel
from app.config import settings
from app.llm.base import BaseLLMProvider
from app.llm.gemini import GeminiProvider
from app.llm.openai import OpenAIProvider
from app.llm.mock_llm import MockLLMProvider

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class LLMService:
    """Unified service for interacting with LLM providers with automatic resilience."""

    def __init__(self, provider_name: Optional[str] = None):
        self.provider_name = (provider_name or settings.LLM_PROVIDER).lower()
        self.provider = self._init_provider()

    def _init_provider(self) -> BaseLLMProvider:
        if self.provider_name == "gemini":
            if settings.GEMINI_API_KEY:
                try:
                    return GeminiProvider(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL)
                except Exception as e:
                    logger.warning("Failed to initialize Gemini provider (%s). Falling back to MockLLM.", e)
            else:
                logger.info("No GEMINI_API_KEY configured. Running in Mock/Offline mode.")
        elif self.provider_name == "openai":
            if settings.OPENAI_API_KEY:
                try:
                    return OpenAIProvider(api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL)
                except Exception as e:
                    logger.warning("Failed to initialize OpenAI provider (%s). Falling back to MockLLM.", e)
            else:
                logger.info("No OPENAI_API_KEY configured. Running in Mock/Offline mode.")

        # Default fallback
        logger.info("Using MockLLMProvider for deterministic offline execution.")
        return MockLLMProvider()

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        delay = 1.0
        for attempt in range(1, max_retries + 1):
            try:
                return self.provider.generate(prompt=prompt, system_prompt=system_prompt, **kwargs)
            except Exception as e:
                logger.warning("LLM generate attempt %d failed: %s", attempt, e)
                if attempt == max_retries:
                    # Final fallback to mock if remote provider fails
                    if not isinstance(self.provider, MockLLMProvider):
                        logger.warning("Remote LLM failed. Falling back to Mock provider.")
                        return MockLLMProvider().generate(prompt=prompt, system_prompt=system_prompt, **kwargs)
                    raise
                time.sleep(delay)
                delay *= 2.0

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        max_retries: int = 3,
        **kwargs
    ) -> T:
        delay = 1.0
        for attempt in range(1, max_retries + 1):
            try:
                return self.provider.generate_structured(
                    prompt=prompt,
                    response_model=response_model,
                    system_prompt=system_prompt,
                    **kwargs
                )
            except Exception as e:
                logger.warning("LLM generate_structured attempt %d failed for %s: %s", attempt, response_model.__name__, e)
                if attempt == max_retries:
                    if not isinstance(self.provider, MockLLMProvider):
                        logger.warning("Remote LLM failed. Falling back to Mock structured response.")
                        return MockLLMProvider().generate_structured(
                            prompt=prompt,
                            response_model=response_model,
                            system_prompt=system_prompt,
                            **kwargs
                        )
                    raise
                time.sleep(delay)
                delay *= 2.0


# Singleton default service instance
llm_service = LLMService()
