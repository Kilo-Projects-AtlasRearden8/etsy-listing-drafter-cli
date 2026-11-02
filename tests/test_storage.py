"""Tests for local JSON storage."""

import json
import os

import pytest

from etsy_drafter.storage import DEFAULT_STORAGE_PATH, DraftNotFoundError, JsonStore


def test_store_round_trip(tmp_path):
    path = tmp_path / "listings.json"
    store = JsonStore(str(path))

    assert store.count() == 0
    assert store.all() == []

    draft_id = store.add({"title": "Mug", "description": "Nice mug", "tags": ["mug"], "item_details": "handmade mug"})
    assert isinstance(draft_id, str)

    drafts = store.all()
    assert len(drafts) == 1
    assert drafts[0]["id"] == draft_id
    assert drafts[0]["title"] == "Mug"
    assert drafts[0]["created_at"]

    fetched = store.get(draft_id)
    assert fetched["title"] == "Mug"

    store.delete(draft_id)
    assert store.count() == 0
    with pytest.raises(DraftNotFoundError):
        store.get(draft_id)
    with pytest.raises(DraftNotFoundError):
        store.delete(draft_id)


def test_store_persists_to_disk(tmp_path):
    path = tmp_path / "listings.json"
    store = JsonStore(str(path))
    store.add({"title": "Mug", "description": "Nice", "tags": [], "item_details": "x"})

    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    assert isinstance(data, list) and data[0]["title"] == "Mug"


def test_store_handles_missing_and_corrupt_file(tmp_path):
    path = tmp_path / "missing.json"
    store = JsonStore(str(path))
    assert store.all() == []

    path.write_text("not json", encoding="utf-8")
    assert store.all() == []


def test_default_storage_path():
    assert DEFAULT_STORAGE_PATH == os.path.expanduser("~/.etsy_drafter/listings.json")
