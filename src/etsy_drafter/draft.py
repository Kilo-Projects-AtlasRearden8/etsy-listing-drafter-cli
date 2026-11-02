"""Prompt templates and drafting logic for Etsy listings."""

from __future__ import annotations

import json
import re
from typing import Any, Mapping

SYSTEM_PROMPT = (
    "You write warm, plain-English Etsy listing titles, descriptions, and tags "
    "like a friend explaining something step by step. Never condescending, "
    "always encouraging. Use beginner-friendly language. Respond with JSON only."
)

DRAFT_PROMPT = """Write an Etsy listing for the item described below.

Item details:
{item_details}

Constraints:
- Title: 140 characters or fewer, front-loaded with the most important keywords, plain English.
- Description: warm and helpful, short paragraphs or bullets, tells the buyer what it is, what it's for, materials, and how to use it. No medical claims, no promises of results.
- Tags: exactly 13 tags, each 20 characters or fewer, lowercase where natural, comma-separated.

Respond with JSON only, using exactly these keys:
{{
  "title": "string",
  "description": "string",
  "tags": ["tag1", "tag2", "..."]
}}"""

_TAG_FALLBACKS = [
    "handmade", "etsy", "gift", "craft", "unique", "artisan", "vintage",
    "accessory", "home", "decor", "jewelry", "clothing", "collectible",
]


def _coerce_tags(value: Any) -> list[str]:
    if isinstance(value, str):
        raw = [tag.strip() for tag in value.split(",") if tag.strip()]
    elif isinstance(value, list):
        raw = [str(tag).strip() for tag in value if str(tag).strip()]
    else:
        raw = []

    seen: set[str] = set()
    tags: list[str] = []
    for tag in raw:
        key = tag.lower()
        if key in seen:
            continue
        seen.add(key)
        tags.append(tag[:20])

    while len(tags) < 13:
        for fallback in _TAG_FALLBACKS:
            if len(tags) >= 13:
                break
            if fallback not in seen:
                tags.append(fallback)
                seen.add(fallback)

    return tags[:13]


def _parse_draft_payload(content: str) -> dict[str, Any]:
    """Parse a JSON draft payload from the model, with light repair."""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Last-resort fallback: treat the whole response as the description.
    return {"title": content[:140], "description": content, "tags": []}


def draft_listing(item_details: str, client) -> dict[str, Any]:
    """Draft title, description, and tags for an Etsy listing.

    Returns a dict with keys title, description, and tags (list of strings),
    without any storage-side metadata.
    """
    if not item_details or not item_details.strip():
        raise ValueError("item_details must not be empty")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": DRAFT_PROMPT.format(item_details=item_details.strip())},
    ]
    content = client.complete(messages)
    payload = _parse_draft_payload(content)

    title = str(payload.get("title", "") or "")[:140]
    description = str(payload.get("description", "") or "")
    tags = _coerce_tags(payload.get("tags", []))

    if not title:
        title = (description or item_details.strip())[:140]

    return {"title": title, "description": description, "tags": tags}
