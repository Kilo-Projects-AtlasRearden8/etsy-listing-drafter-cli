"""Tests for CSV export."""

from etsy_drafter.export import export_csv


def test_export_csv_writes_expected_columns(tmp_path):
    drafts = [
        {
            "id": "abc-1",
            "created_at": "2026-01-01T00:00:00+00:00",
            "title": "Hand-Knit Scarf",
            "description": "Warm and cozy.",
            "tags": ["wool scarf", "hand knit", "winter"],
            "item_details": "cream wool scarf",
        },
        {
            "id": "abc-2",
            "created_at": "2026-01-02T00:00:00+00:00",
            "title": "Mug",
            "description": "Handmade mug.",
            "tags": "mug, pottery",
            "item_details": "handmade mug",
        },
    ]
    out = tmp_path / "listings.csv"
    rows_written = export_csv(drafts, str(out))

    assert rows_written == 2
    text = out.read_text(encoding="utf-8")
    lines = text.strip().splitlines()
    assert lines[0] == "id,created_at,title,description,tags,item_details"
    assert lines[1].startswith("abc-1,2026-01-01T00:00:00+00:00,Hand-Knit Scarf")
    assert "wool scarf; hand knit; winter" in lines[1]
    assert lines[2].startswith("abc-2,2026-01-02T00:00:00+00:00,Mug")
    assert "mug, pottery" in lines[2]


def test_export_empty_writes_header_only(tmp_path):
    out = tmp_path / "empty.csv"
    rows_written = export_csv([], str(out))
    assert rows_written == 0
    assert out.read_text(encoding="utf-8").strip() == "id,created_at,title,description,tags,item_details"
