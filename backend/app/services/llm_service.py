import json
import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class LLMServiceError(Exception):
    """
    Raised when the external LLM call fails or returns invalid content.
    """


def _extract_json_from_text(text: str) -> dict[str, Any]:
    """
    Extracts JSON from normal text or markdown-wrapped JSON.

    Supports:
    - raw JSON
    - ```json ... ```
    - ``` ... ```
    """
    cleaned = text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.removeprefix("```json").strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```").strip()

    if cleaned.endswith("```"):
        cleaned = cleaned.removesuffix("```").strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse LLM JSON output: %s", cleaned)
        raise LLMServiceError("LLM returned invalid JSON") from exc

    if not isinstance(parsed, dict):
        raise LLMServiceError("LLM JSON output must be an object")

    return parsed


def call_openai_compatible_chat_completion(
    *,
    system_prompt: str,
    user_prompt: str,
) -> dict[str, Any]:
    """
    Calls an OpenAI-compatible chat completion endpoint.

    Works with OpenAI-compatible providers by changing:
    - LLM_BASE_URL
    - LLM_API_KEY
    - LLM_MODEL
    """
    if not settings.has_llm_api_key:
        raise LLMServiceError("LLM_API_KEY is missing")

    base_url = settings.llm_base_url.rstrip("/")
    url = f"{base_url}/chat/completions"

    payload = {
        "model": settings.llm_model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }

    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.exception("LLM request failed")
        raise LLMServiceError("LLM request failed") from exc

    data = response.json()

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        logger.error("Unexpected LLM response shape: %s", data)
        raise LLMServiceError("Unexpected LLM response shape") from exc

    return _extract_json_from_text(content)