"""Integration tests against a mock OpenAI-compatible HTTP endpoint.

A real ThreadingHTTPServer is bound to localhost on an ephemeral port and
answers POST /v1/chat/completions, so the client is exercised end to end
without any real LLM or API key.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from etsy_drafter.__main__ import main


MOCK_DRAFT = {
    "title": "Hand-Knit Wool Scarf - Cream",
    "description": "A cozy, hand-knit wool scarf in cream, about 60 inches long. "
                   "Perfect for chilly days and handmade gifts.",
    "tags": ["wool scarf", "hand knit", "cream scarf", "winter accessory", "gift",
             "knitted", "cozy", "wool", "handmade", "warm", "neckwear", "accessory",
             "cold weather"],
}


class MockHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length)  # consume request body (not asserted here)

        body = json.dumps({
            "id": "chatcmpl-mock",
            "object": "chat.completion",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": json.dumps(MOCK_DRAFT)},
                "finish_reason": "stop",
            }],
        }).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # silence server logs
        pass


@pytest.fixture
def mock_endpoint():
    server = ThreadingHTTPServer(("127.0.0.1", 0), MockHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        port = server.server_address[1]
        yield f"http://127.0.0.1:{port}/v1"
    finally:
        server.shutdown()
        server.server_close()


def test_draft_against_mock_endpoint(tmp_path, mock_endpoint):
    storage = tmp_path / "listings.json"
    exit_code = main([
        "draft",
        "--details", "A cream hand-knit wool scarf, about 60 inches long.",
        "--base-url", mock_endpoint,
        "--model", "mock-model",
        "--storage", str(storage),
    ])
    assert exit_code == 0

    drafts = json.loads(storage.read_text(encoding="utf-8"))
    assert len(drafts) == 1
    draft = drafts[0]
    assert draft["title"] == MOCK_DRAFT["title"]
    assert draft["description"] == MOCK_DRAFT["description"]
    assert draft["tags"] == MOCK_DRAFT["tags"]
    assert draft["item_details"] == "A cream hand-knit wool scarf, about 60 inches long."
    assert draft["id"] and draft["created_at"]


def test_export_after_draft_against_mock_endpoint(tmp_path, mock_endpoint):
    storage = tmp_path / "listings.json"
    csv_out = tmp_path / "listings.csv"

    assert main(["draft", "--details", "cream wool scarf", "--base-url", mock_endpoint,
                 "--storage", str(storage)]) == 0
    assert main(["export", "--out", str(csv_out), "--storage", str(storage)]) == 0

    text = csv_out.read_text(encoding="utf-8")
    assert "Hand-Knit Wool Scarf - Cream" in text
    assert "wool scarf; hand knit" in text
