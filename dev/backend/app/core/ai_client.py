"""
Shared AI client for aws-gpt-5.4 (OpenAI-compatible streaming endpoint).
Base URL: http://3.27.111.18:8080/api/v1  (server requires stream=True)
All routers import from here so config is in one place.
Falls back gracefully (returns None) if the AI service is unavailable.
"""

from openai import OpenAI
from app.core.config import settings

_client: OpenAI | None = None


def get_ai_client() -> OpenAI:
    global _client
    if _client is None:
        # Strip trailing /v1 if present in BASE_URL, then add /v1 ourselves
        # so the SDK forms the correct path: <base>/chat/completions
        base = settings.AWS_GPT_BASE_URL.rstrip("/")
        if not base.endswith("/v1"):
            base = base + "/v1"
        _client = OpenAI(base_url=base, api_key=settings.AWS_GPT_API_KEY)
    return _client


def chat(
    system: str,
    user: str,
    temperature: float = 0.2,
    max_tokens: int = 2048,
) -> str | None:
    """
    Send a streaming chat completion request to aws-gpt-5.4.
    Returns the full assistant reply as a string, or None on any error.
    Callers fall back to their own mock/heuristic data when None is returned.
    """
    try:
        client = get_ai_client()
        stream = client.chat.completions.create(
            model=settings.AWS_GPT_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,          # server requires streaming
        )
        result = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                result += delta
        return result
    except Exception:
        return None
