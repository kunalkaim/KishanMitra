import os
import abc
from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.rag.generation.gemini_provider import (
    GeminiProvider,
    GeminiAuthError,
    GeminiQuotaError,
    GeminiTransientError,
    GeminiProviderError
)


class BaseLLMProvider(abc.ABC):
    @abc.abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 800) -> Any:
        pass

    @property
    @abc.abstractmethod
    def provider_name(self) -> str:
        pass


class GeminiLLMProvider(BaseLLMProvider):
    """
    Adapter integrating the dedicated GeminiProvider with Google's official google-genai SDK.
    Supports structured agricultural output parsing and source citation tags.
    """
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        target_model = model_name or getattr(settings, "RAG_LLM_MODEL", "gemini-3.5-flash-lite")
        self.provider = GeminiProvider(
            api_key=api_key,
            model_name=target_model,
            timeout_seconds=35,
            max_output_tokens=900,
            temperature=0.2,
            max_retries=2
        )

    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 800) -> Dict[str, Any]:
        return self.provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=max_tokens
        )

    @property
    def is_configured(self) -> bool:
        return self.provider.is_configured

    @property
    def provider_name(self) -> str:
        return self.provider.provider_name


class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini", base_url: Optional[str] = None):
        from openai import OpenAI
        self._model = model_name
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 800) -> Dict[str, Any]:
        resp = self.client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.2
        )
        content = resp.choices[0].message.content.strip()
        return {
            "answer": content,
            "language": "en",
            "citation_ids": [],
            "evidence_sufficiency": "sufficient",
            "follow_up_questions": []
        }

    @property
    def provider_name(self) -> str:
        return f"OpenAI ({self._model})"


class RetrievalOnlyLLMProvider(BaseLLMProvider):
    """
    Fallback provider when no external LLM API key is configured or provider is unavailable.
    Directly formats retrieved verified evidence passages with page citations.
    """
    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 800) -> str:
        return "RETRIEVAL_ONLY_MODE"

    @property
    def provider_name(self) -> str:
        return "Retrieval-Only Mode (Evidence Citation Engine)"


def get_llm_provider() -> BaseLLMProvider:
    """
    Detects and returns configured LLM provider or Retrieval-Only fallback.
    Prioritizes Google Gemini per KisanMitra Phase 4.1 specification.
    """
    rag_provider = (os.getenv("RAG_LLM_PROVIDER") or getattr(settings, "RAG_LLM_PROVIDER", None) or "gemini").lower()
    rag_model = os.getenv("RAG_LLM_MODEL") or getattr(settings, "RAG_LLM_MODEL", None) or "gemini-3.5-flash-lite"

    # 1. Primary: Google Gemini
    if "gemini" in rag_provider:
        gemini_key = (
            os.getenv("GEMINI_API_KEY") or
            os.getenv("GOOGLE_API_KEY") or
            getattr(settings, "GEMINI_API_KEY", None) or
            os.getenv("RAG_LLM_API_KEY")
        )
        if gemini_key:
            return GeminiLLMProvider(api_key=gemini_key, model_name=rag_model)

    # 2. Secondary: OpenAI (if explicitly configured)
    if "openai" in rag_provider:
        openai_key = os.getenv("OPENAI_API_KEY") or os.getenv("RAG_LLM_API_KEY")
        rag_base = os.getenv("RAG_LLM_BASE_URL")
        if openai_key and not openai_key.startswith("sk-proj-placeholder"):
            return OpenAILLMProvider(api_key=openai_key, model_name=rag_model, base_url=rag_base)

    # 3. Transparent Retrieval-Only Fallback
    return RetrievalOnlyLLMProvider()
