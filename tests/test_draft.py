"""Tests for draft generation logic."""

import json

import pytest

from etsy_drafter.draft import draft_listing


class FakeClient:
    def __init__(self, content):
        self.content = content
        self.calls = []

    def complete(self, messages, temperature=0.7, max_tokens=500):
        self.calls.append((messages, temperature, max_tokens))
        return self.content


def test_draft_listing_parses_json_payload():
    client = FakeClient(json.dumps({
        "title": "Hand-Knit Wool Scarf - Cozy Winter Accessory",
        "description": "A warm, hand-knit wool scarf for chilly days.",
        "tags": ["wool scarf", "hand knit", "winter accessory"],
    }))
    result = draft_listing("A hand-knit wool scarf in cream, about 60 inches long.", client)

    assert result["title"] == "Hand-Knit Wool Scarf - Cozy Winter Accessory"
    assert "hand-knit wool scarf" in result["description"].lower()
    assert result["tags"] == ["wool scarf", "hand knit", "winter accessory"]
    assert len(client.calls) == 1
    assert "hand-knit wool scarf" in client.calls[0][0][1]["content"]


def test_draft_listing_truncates_title_to_140_chars():
    long_title = "x" * 200
    client = FakeClient(json.dumps({"title": long_title, "description": "desc", "tags": []}))
    result = draft_listing("item", client)
    assert len(result["title"]) == 140


def test_draft_listing_caps_tags_at_thirteen():
    tags = [f"tag {i}" for i in range(20)]
    client = FakeClient(json.dumps({"title": "t", "description": "d", "tags": tags}))
    result = draft_listing("item", client)
    assert len(result["tags"]) == 13


def test_draft_listing_handles_comma_string_tags():
    client = FakeClient(json.dumps({"title": "t", "description": "d", "tags": "one, two, three"}))
    result = draft_listing("item", client)
    assert result["tags"] == ["one", "two", "three"]


def test_draft_listing_falls_back_to_description_when_title_missing():
    client = FakeClient(json.dumps({"description": "A lovely handmade mug.", "tags": []}))
    result = draft_listing("A lovely handmade mug.", client)
    assert result["title"] == "A lovely handmade mug."


def test_draft_listing_repairs_json_with_extra_text():
    client = FakeClient("Here is your listing:\n{\"title\": \"Mug\", \"description\": \"Nice mug\", \"tags\": [\"mug\"]}\nHope it helps!")
    result = draft_listing("mug", client)
    assert result["title"] == "Mug"


def test_draft_listing_raises_on_empty_details():
    with pytest.raises(ValueError):
        draft_listing("", FakeClient("{}"))
    with pytest.raises(ValueError):
        draft_listing("   ", FakeClient("{}"))
