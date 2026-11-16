import os
import re
import json
import time
import asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from google import genai
from google.genai import types
from google.genai import errors as genai_errors


class GeminiAgriculturalResponse(BaseModel):
    answer: str = Field(..., description="Evidence-grounded agricultural answer for the farmer")
    language: str = Field(default="en", description="Detected or response language ('en', 'hi', or 'bilingual')")
    citation_ids: List[str] = Field(default_factory=list, description="Source identifiers cited, e.g. ['S1', 'S2']")
    evidence_sufficiency: str = Field(default="sufficient", description="'sufficient', 'partial', or 'insufficient'")
    follow_up_questions: List[str] = Field(default_factory=list, description="Suggested practical follow-up questions")


class GeminiProviderError(Exception):
    """Base exception for Gemini provider errors."""
    pass


class GeminiAuthError(GeminiProviderError):
    """Raised when API key is missing or authentication fails."""
    pass


class GeminiQuotaError(GeminiProviderError):
    """Raised when rate limits (429) or quota is exhausted."""
    pass


class GeminiTransientError(GeminiProviderError):
    """Raised when temporary service unavailability (503/504) persists after retries."""
    pass


class GeminiProvider:
    """
    Dedicated Google Gemini LLM generation service for KisanMitra RAG.
    Powered by Google's official `google-genai` Python SDK.
    Features:
    - Thread-safe non-blocking async generation
    - Structured JSON generation with Pydantic validation
    - Source identifier extraction ([S1], [S2])
    - Bounded exponential backoff on transient service errors
    - Sanitized logging that never leaks API credentials
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout_seconds: int = 35,
        max_output_tokens: int = 900,
        temperature: float = 0.2,
        max_retries: int = 2
    ):
        self._api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model_name = model_name or os.getenv("RAG_LLM_MODEL") or "gemini-3.5-flash-lite"
        self.timeout_seconds = timeout_seconds
        self.max_output_tokens = max_output_tokens
        self.temperature = temperature
        self.max_retries = max_retries

        self._client: Optional[genai.Client] = None
        if self._api_key:
            try:
                self._client = genai.Client(
                    api_key=self._api_key,
                    http_options=types.HttpOptions(timeout=int(self.timeout_seconds * 1000))
                )
            except Exception as e:
                sanitized = self._sanitize_error(str(e))
                print(f"[GeminiProvider] Warning during initialization: {sanitized}")

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key and self._client)

    @property
    def provider_name(self) -> str:
        return f"Google Gemini ({self.model_name})"

    def _sanitize_error(self, message: str) -> str:
        if self._api_key and len(self._api_key) > 5:
            return message.replace(self._api_key, "[REDACTED_API_KEY]")
        return message

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Synchronous call to generate structured agricultural response from Gemini.
        Returns parsed dictionary with answer, citations, and metadata.
        """
        if not self.is_configured:
            raise GeminiAuthError(
                "Gemini API key is not configured. Please set GEMINI_API_KEY in the environment."
            )

        tokens = max_tokens or self.max_output_tokens

        # Structured schema instruction appended to prompt
        json_instruction = (
            "\n\nCRITICAL OUTPUT REQUIREMENT:\n"
            "You MUST respond ONLY with a valid, parseable JSON object matching this schema:\n"
            "{\n"
            '  "answer": "Your detailed, respectful, and grounded agricultural guidance in the farmer\'s language...",\n'
            '  "language": "hi" or "en",\n'
            '  "citation_ids": ["S1", "S2"],\n'
            '  "evidence_sufficiency": "sufficient" or "partial" or "insufficient",\n'
            '  "follow_up_questions": ["Question 1?", "Question 2?"]\n'
            "}\n"
            "Do not include any code block ticks, backticks, or text before or after the JSON."
        )

        full_prompt = f"{system_prompt}{json_instruction}\n\n{user_prompt}"

        config = types.GenerateContentConfig(
            temperature=self.temperature,
            max_output_tokens=tokens,
            response_mime_type="application/json"
        )

        active_model = self.model_name
        last_error = None
        for attempt in range(1, self.max_retries + 2):
            try:
                start_time = time.time()
                response = self._client.models.generate_content(
                    model=active_model,
                    contents=full_prompt,
                    config=config
                )
                latency = round(time.time() - start_time, 2)
                raw_text = response.text.strip() if response and response.text else ""

                # Parse JSON response
                parsed = self._parse_structured_response(raw_text)
                parsed["latency_seconds"] = latency
                parsed["model_name"] = active_model
                parsed["usage"] = {
                    "prompt_token_count": getattr(response.usage_metadata, "prompt_token_count", 0) if hasattr(response, "usage_metadata") else 0,
                    "candidates_token_count": getattr(response.usage_metadata, "candidates_token_count", 0) if hasattr(response, "usage_metadata") else 0,
                }
                return parsed

            except Exception as exc:
                last_error = exc
                err_str = self._sanitize_error(str(exc))
                err_lower = err_str.lower()

                # 1. Non-retryable authentication error
                if any(k in err_lower for k in ["401", "403", "unauthenticated", "permission_denied", "api_key_invalid"]):
                    raise GeminiAuthError(f"Gemini authentication failed: {err_str}")

                # 2. Non-retryable quota error
                if "429" in err_lower or "resource_exhausted" in err_lower or "quota" in err_lower:
                    raise GeminiQuotaError(f"Gemini rate limit or quota exceeded: {err_str}")

                # 3. Model not found error
                if "404" in err_lower and "not_found" in err_lower:
                    raise GeminiProviderError(f"Gemini model '{active_model}' not available on current API version: {err_str}")

                # 4. Retryable transient errors (503 UNAVAILABLE, 504 DEADLINE_EXCEEDED, network glitches)
                if attempt <= self.max_retries and any(k in err_lower for k in ["503", "504", "deadline_exceeded", "unavailable", "timeout"]):
                    if "503" in err_lower and active_model != "gemini-3.5-flash-lite":
                        active_model = "gemini-3.5-flash-lite"
                        print("[GeminiProvider] 503 high demand on primary model. Failing over to gemini-3.5-flash-lite...")
                    sleep_time = (2 ** attempt) + 0.5
                    print(f"[GeminiProvider] Transient error on attempt {attempt}/{self.max_retries + 1}: {err_str[:120]}. Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                    continue

                # Stop retrying on unexpected errors
                break

        # If all retries exhausted
        raise GeminiTransientError(f"Gemini service failed after {self.max_retries + 1} attempts: {self._sanitize_error(str(last_error))}")

    async def generate_async(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Runs synchronous generate in a background thread to avoid blocking FastAPI event loop."""
        return await asyncio.to_thread(
            self.generate,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=max_tokens
        )

    def _parse_structured_response(self, text: str) -> Dict[str, Any]:
        """Safely parses and validates JSON output, with resilient fallback."""
        clean_text = text.strip()
        # Remove markdown JSON fences if model returned them
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()

        try:
            data = json.loads(clean_text)
            validated = GeminiAgriculturalResponse.model_validate(data)
            return validated.model_dump()
        except Exception:
            # Fallback recovery: extract text and citation tags [S1], [S2] via regex
            citations_found = list(set(re.findall(r'\[S(\d+)\]', clean_text)))
            mapped_citations = [f"S{c}" for c in sorted(citations_found, key=int)] if citations_found else []
            
            # Detect language
            has_devanagari = bool(re.search(r'[\u0900-\u097F]', clean_text))
            
            return {
                "answer": clean_text,
                "language": "hi" if has_devanagari else "en",
                "citation_ids": mapped_citations,
                "evidence_sufficiency": "sufficient",
                "follow_up_questions": [
                    "What are the recommended fertilizer doses for this stage?",
                    "How to manage pest attacks organically?",
                    "What are the prevailing mandi prices for this crop?"
                ]
            }
