"""Local JSON storage for Etsy listing drafts.

Drafts are stored as a JSON list on disk. Writes are atomic (temp file +
os.replace) so concurrent crashes cannot corrupt the store.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any

DEFAULT_STORAGE_PATH = os.path.expanduser("~/.etsy_drafter/listings.json")


class DraftNotFoundError(KeyError):
    """Raised when a draft id does not exist in the store."""


class JsonStore:
    """Append-only JSON store of listing drafts."""

    def __init__(self, path: str | None = None) -> None:
        self.path = path or os.environ.get("ETSY_DRAFTER_STORAGE") or DEFAULT_STORAGE_PATH
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)

    def _read_all(self) -> list[dict[str, Any]]:
        if not os.path.exists(self.path):
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (json.JSONDecodeError, OSError):
            return []
        if not isinstance(data, list):
            return []
        return [entry for entry in data if isinstance(entry, dict)]

    def _write_all(self, drafts: list[dict[str, Any]]) -> None:
        directory = os.path.dirname(os.path.abspath(self.path)) or "."
        tmp_path = os.path.join(directory, f".{os.path.basename(self.path)}.tmp")
        with open(tmp_path, "w", encoding="utf-8") as handle:
            json.dump(drafts, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(tmp_path, self.path)

    def add(self, draft: Mapping[str, Any]) -> str:
        """Save a draft and return its id."""
        now = datetime.now(timezone.utc).isoformat()
        entry = dict(draft)
        entry.setdefault("id", str(uuid.uuid4()))
        entry.setdefault("created_at", now)
        drafts = self._read_all()
        drafts.append(entry)
        self._write_all(drafts)
        return str(entry["id"])

    def all(self) -> list[dict[str, Any]]:
        """Return every stored draft."""
        return self._read_all()

    def get(self, draft_id: str) -> dict[str, Any]:
        """Return a single draft by id, or raise DraftNotFoundError."""
        for entry in self._read_all():
            if str(entry.get("id")) == draft_id:
                return entry
        raise DraftNotFoundError(f"Draft not found: {draft_id}")

    def delete(self, draft_id: str) -> None:
        """Remove a draft by id; raises DraftNotFoundError if missing."""
        drafts = self._read_all()
        remaining = [entry for entry in drafts if str(entry.get("id")) != draft_id]
        if len(remaining) == len(drafts):
            raise DraftNotFoundError(f"Draft not found: {draft_id}")
        self._write_all(remaining)

    def count(self) -> int:
        return len(self._read_all())
