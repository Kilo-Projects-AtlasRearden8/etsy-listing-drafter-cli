"""Command-line interface for the Etsy listing drafter."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Sequence

from .client import DEFAULT_BASE_URL, DEFAULT_MODEL, LLMClient, LLMError
from .draft import draft_listing
from .export import export_csv
from .storage import DEFAULT_STORAGE_PATH, DraftNotFoundError, JsonStore


def _prompt(message: str) -> str:
    try:
        return input(message).strip()
    except EOFError:
        return ""


def _collect_item_details(args: argparse.Namespace) -> str:
    if args.details:
        return args.details
    if args.details_file:
        try:
            with open(args.details_file, "r", encoding="utf-8") as handle:
                return handle.read().strip()
        except OSError as error:
            print(f"error: could not read {args.details_file}: {error}", file=sys.stderr)
            sys.exit(2)

    print("Tell me about your item (blank line when done):")
    lines: list[str] = []
    while True:
        line = _prompt("> ")
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def _build_client(args: argparse.Namespace) -> LLMClient:
    return LLMClient(
        base_url=getattr(args, "base_url", None),
        model=getattr(args, "model", None),
    )


def _print_draft(draft: dict[str, object], index: int | None = None) -> None:
    label = f" [{index}]" if index is not None else ""
    print(f"{'=' * 60}\nDraft{label}\n{'=' * 60}")
    print(f"Title: {draft.get('title', '')}")
    print(f"\nDescription:\n{draft.get('description', '')}")
    tags = draft.get("tags", [])
    if isinstance(tags, list):
        tags_field = ", ".join(str(tag) for tag in tags)
    else:
        tags_field = str(tags)
    print(f"\nTags: {tags_field}")


def cmd_draft(args: argparse.Namespace) -> int:
    item_details = _collect_item_details(args)
    if not item_details:
        print("error: no item details provided", file=sys.stderr)
        return 2

    try:
        client = _build_client(args)
        draft = draft_listing(item_details, client)
    except LLMError as error:
        print(f"error: {error}", file=sys.stderr)
        print("tip: start Ollama (ollama serve) and pull a model, e.g. 'ollama pull llama3.2'", file=sys.stderr)
        print("tip: override the endpoint with ETSY_DRAFTER_BASE_URL or --base-url", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    draft["item_details"] = item_details
    store = JsonStore(getattr(args, "storage", None))
    draft_id = store.add(draft)
    draft["id"] = draft_id

    _print_draft(draft)
    print(f"\nSaved draft id {draft_id} to {store.path}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    store = JsonStore(getattr(args, "storage", None))
    drafts = store.all()
    if not drafts:
        print("No drafts stored yet. Run: etsy-drafter draft")
        return 0
    for index, draft in enumerate(drafts, start=1):
        title = str(draft.get("title", ""))[:60]
        tags = draft.get("tags", [])
        tags_field = ", ".join(str(tag) for tag in tags) if isinstance(tags, list) else str(tags)
        print(f"{index}. [{draft.get('id', '')}] {draft.get('created_at', '')}")
        print(f"    {title}")
        print(f"    tags: {tags_field}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    store = JsonStore(getattr(args, "storage", None))
    drafts = store.all()
    try:
        rows_written = export_csv(drafts, args.out)
    except OSError as error:
        print(f"error: could not write {args.out}: {error}", file=sys.stderr)
        return 1
    print(f"Exported {rows_written} draft(s) to {args.out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="etsy-drafter",
        description="Draft Etsy listing titles, descriptions, and tags from item details "
        "using a local OpenAI-compatible endpoint (default Ollama).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s 0.1.0",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    draft_parser = subparsers.add_parser("draft", help="Draft a new Etsy listing")
    draft_parser.add_argument("--details", help="Item details as text")
    draft_parser.add_argument("--details-file", help="Path to a file containing item details")
    draft_parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="OpenAI-compatible endpoint base URL")
    draft_parser.add_argument("--model", default=DEFAULT_MODEL, help="Model name")
    draft_parser.add_argument("--storage", default=DEFAULT_STORAGE_PATH, help="JSON storage path")
    draft_parser.set_defaults(func=cmd_draft)

    list_parser = subparsers.add_parser("list", help="List stored drafts")
    list_parser.add_argument("--storage", default=DEFAULT_STORAGE_PATH, help="JSON storage path")
    list_parser.set_defaults(func=cmd_list)

    export_parser = subparsers.add_parser("export", help="Export stored drafts to CSV")
    export_parser.add_argument("--out", required=True, help="Output CSV path")
    export_parser.add_argument("--storage", default=DEFAULT_STORAGE_PATH, help="JSON storage path")
    export_parser.set_defaults(func=cmd_export)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
