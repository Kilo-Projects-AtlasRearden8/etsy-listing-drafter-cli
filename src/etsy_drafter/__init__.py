"""Etsy listing drafter CLI.

Drafts Etsy listing titles, descriptions, and tags from item details using a
configurable OpenAI-compatible endpoint (default Ollama). Local-first: JSON
storage on disk, no API keys, no secrets.
"""

__version__ = "0.1.0"

from .client import LLMClient, LLMError
from .draft import draft_listing
from .export import export_csv
from .storage import JsonStore, DraftNotFoundError

__all__ = ["LLMClient", "LLMError", "draft_listing", "export_csv", "JsonStore", "DraftNotFoundError"]
