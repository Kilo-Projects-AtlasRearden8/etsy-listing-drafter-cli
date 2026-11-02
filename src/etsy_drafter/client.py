"""Client for OpenAI-compatible chat completion endpoints (Ollama by default).

Uses only the Python standard library so the tool runs with no dependencies
and no API keys. Endpoint and model are configurable via constructor arguments
or environment variables.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Iterable, Mapping

DEFAULT_BASE_URL = "http://localhost:11434/v1"
DEFAULT_MODEL = "llama3.2"
DEFAULT_TIMEOUT = 60


class LLMError(RuntimeError):
    """Raised when the LLM endpoint returns an error or invalid response."""


class LLMClient:
    """Thin client over an OpenAI-compatible /v1/chat/completions endpoint."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
    ) -> None:
        self.base_url = (base_url or os.environ.get("ETSY_DRAFTER_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.model = model or os.environ.get("ETSY_DRAFTER_MODEL") or DEFAULT_MODEL
        self.timeout = timeout if timeout is not None else int(os.environ.get("ETSY_DRAFTER_TIMEOUT", str(DEFAULT_TIMEOUT)))

    def complete(
        self,
        messages: Iterable[Mapping[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """POST a chat completion and return the assistant message content."""
        payload = {
            "model": self.model,
            "messages": [dict(m) for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace") if hasattr(error, "read") else ""
            raise LLMError(f"LLM endpoint returned HTTP {error.code}: {detail}") from error
        except urllib.error.URLError as error:
            raise LLMError(f"Could not reach LLM endpoint at {self.base_url}: {error}") from error

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as error:
            raise LLMError(f"LLM endpoint returned invalid JSON: {raw[:200]}") from error

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise LLMError(f"LLM endpoint returned unexpected response shape: {data!r}") from error

        if not isinstance(content, str):
            raise LLMError(f"LLM endpoint returned non-string content: {content!r}")
        return content.strip()
