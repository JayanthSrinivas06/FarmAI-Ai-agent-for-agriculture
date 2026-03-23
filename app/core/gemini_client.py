"""
Gemini AI client – lazy singleton using the new google-genai SDK.

The client is created on first use so the server can start even if
GEMINI_API_KEY is not yet in the environment (it gets loaded from .env
by main.py before any request arrives).
"""
from __future__ import annotations
from google import genai
from app.core.config import get_gemini_api_key

_client: genai.Client | None = None


def get_gemini_client() -> genai.Client:
    """Return the shared Gemini client, creating it on first call."""
    global _client
    if _client is None:
        key = get_gemini_api_key()
        if not key:
            raise ValueError(
                "GEMINI_API_KEY is not set. "
                "Add it to your .env file:  GEMINI_API_KEY=your_key_here"
            )
        _client = genai.Client(api_key=key)
    return _client
