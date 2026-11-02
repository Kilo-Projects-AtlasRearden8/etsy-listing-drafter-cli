"""CSV export for stored Etsy listing drafts."""

from __future__ import annotations

import csv
from typing import Iterable, Mapping

COLUMNS = ["id", "created_at", "title", "description", "tags", "item_details"]


def export_csv(drafts: Iterable[Mapping[str, object]], path: str) -> int:
    """Write drafts to a CSV file and return the number of rows written."""
    rows_written = 0
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(COLUMNS)
        for draft in drafts:
            tags = draft.get("tags", [])
            if isinstance(tags, str):
                tags_field = tags
            else:
                tags_field = "; ".join(str(tag) for tag in tags)
            writer.writerow(
                [
                    draft.get("id", ""),
                    draft.get("created_at", ""),
                    draft.get("title", ""),
                    draft.get("description", ""),
                    tags_field,
                    draft.get("item_details", ""),
                ]
            )
            rows_written += 1
    return rows_written
