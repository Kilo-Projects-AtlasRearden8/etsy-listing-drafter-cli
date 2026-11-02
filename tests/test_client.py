"""Unit tests for the OpenAI-compatible LLM client."""

import json
import urllib.error
from unittest import mock

import pytest

from etsy_drafter.client import DEFAULT_BASE_URL, DEFAULT_MODEL, LLMClient, LLMError


def _make_client(**overrides):
    return LLMClient(base_url=overrides.get("base_url", "http://localhost:11434/v1"),
                     model=overrides.get("model", "llama3.2"))


def test_complete_posts_to_chat_completions_and_returns_content():
    payload = {"choices": [{"message": {"role": "assistant", "content": "Hand-Knit Wool Scarf"}}]}
    response_body = json.dumps(payload).encode("utf-8")

    class FakeResponse:
        status = 200

        def read(self):
            return response_body

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    captured = {}

    def fake_urlopen(request, timeout=None):
        captured["url"] = request.full_url
        captured["method"] = request.method
        captured["headers"] = {k: v for k, v in request.headers.items()}
        captured["body"] = json.loads(request.data.decode("utf-8")) if request.data else None
        captured["timeout"] = timeout
        return FakeResponse()

    with mock.patch("etsy_drafter.client.urllib.request.urlopen", side_effect=fake_urlopen):
        client = _make_client()
        content = client.complete([{"role": "user", "content": "Draft a title"}])

    assert content == "Hand-Knit Wool Scarf"
    assert captured["url"] == "http://localhost:11434/v1/chat/completions"
    assert captured["method"] == "POST"
    headers = {k.lower(): v for k, v in captured["headers"].items()}
    assert headers["content-type"] == "application/json"
    assert captured["body"]["model"] == "llama3.2"
    assert captured["body"]["messages"] == [{"role": "user", "content": "Draft a title"}]
    assert captured["timeout"] == 60


def test_complete_uses_env_overrides(monkeypatch):
    monkeypatch.setenv("ETSY_DRAFTER_BASE_URL", "http://127.0.0.1:9999/v1")
    monkeypatch.setenv("ETSY_DRAFTER_MODEL", "mistral")
    monkeypatch.setenv("ETSY_DRAFTER_TIMEOUT", "25")

    captured = {}

    class FakeResponse:
        def read(self):
            return json.dumps({"choices": [{"message": {"content": "ok"}}]}).encode()

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def fake_urlopen(request, timeout=None):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        return FakeResponse()

    with mock.patch("etsy_drafter.client.urllib.request.urlopen", side_effect=fake_urlopen):
        client = LLMClient()
        assert client.base_url == "http://127.0.0.1:9999/v1"
        assert client.model == "mistral"
        assert client.timeout == 25
        client.complete([{"role": "user", "content": "hi"}])

    assert captured["url"] == "http://127.0.0.1:9999/v1/chat/completions"
    assert captured["timeout"] == 25


def test_complete_http_error_raises_llm_error():
    def fake_urlopen(request, timeout=None):
        raise urllib.error.HTTPError("http://localhost:11434/v1/chat/completions", 502, "bad gateway", {}, None)

    with mock.patch("etsy_drafter.client.urllib.request.urlopen", side_effect=fake_urlopen):
        with pytest.raises(LLMError, match="HTTP 502"):
            _make_client().complete([{"role": "user", "content": "hi"}])


def test_complete_unreachable_raises_llm_error():
    import urllib.error

    def fake_urlopen(request, timeout=None):
        raise urllib.error.URLError("connection refused")

    with mock.patch("etsy_drafter.client.urllib.request.urlopen", side_effect=fake_urlopen):
        with pytest.raises(LLMError, match="Could not reach LLM endpoint"):
            _make_client().complete([{"role": "user", "content": "hi"}])


def test_complete_bad_json_raises_llm_error():
    class FakeResponse:
        def read(self):
            return b"not json"

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    with mock.patch("etsy_drafter.client.urllib.request.urlopen", return_value=FakeResponse()):
        with pytest.raises(LLMError, match="invalid JSON"):
            _make_client().complete([{"role": "user", "content": "hi"}])


def test_complete_bad_shape_raises_llm_error():
    class FakeResponse:
        def read(self):
            return json.dumps({"choices": []}).encode()

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    with mock.patch("etsy_drafter.client.urllib.request.urlopen", return_value=FakeResponse()):
        with pytest.raises(LLMError, match="unexpected response shape"):
            _make_client().complete([{"role": "user", "content": "hi"}])


def test_defaults():
    client = _make_client()
    assert client.base_url == DEFAULT_BASE_URL
    assert client.model == DEFAULT_MODEL
