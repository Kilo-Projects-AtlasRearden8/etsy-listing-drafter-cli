# STATUS

## What was built

`etsy-listing-drafter-cli` — a local-first Python CLI that drafts Etsy listing
titles, descriptions, and tags from item details, for Dylan Asdale /
Asdale Dynamics, LLC.

- `src/etsy_drafter/client.py` — stdlib-only (`urllib`) client for
  OpenAI-compatible `/v1/chat/completions` endpoints. Defaults to Ollama at
  `http://localhost:11434/v1`, model `llama3.2`. Endpoint, model, and timeout
  configurable via CLI flags or `ETSY_DRAFTER_BASE_URL` /
  `ETSY_DRAFTER_MODEL` / `ETSY_DRAFTER_TIMEOUT`. Clean error messages when the
  endpoint is unreachable or returns bad data. No API keys, no secrets.
- `src/etsy_drafter/draft.py` — prompt templates (warm, plain English, beginner
  friendly, never condescending) and drafting logic: title ≤140 chars,
  description, exactly 13 tags ≤20 chars each. Repairs imperfect model JSON
  output; falls back sensibly.
- `src/etsy_drafter/storage.py` — local JSON storage
  (`~/.etsy_drafter/listings.json`, overridable via `ETSY_DRAFTER_STORAGE` or
  `--storage`). Atomic writes (temp file + `os.replace`), UUID ids, UTC
  timestamps, add/list/get/delete/count.
- `src/etsy_drafter/export.py` — CSV export
  (`id, created_at, title, description, tags, item_details`; tags joined with
  `; `).
- `src/etsy_drafter/__main__.py` — argparse CLI: `draft` (interactive or
  `--details` / `--details-file`), `list`, `export --out`.
- `tests/` — 23 tests: client unit tests (mocked `urlopen`), draft logic,
  storage round trip, CSV export, CLI surface, and an integration test against
  a real mock HTTP endpoint on localhost (`tests/test_mock_endpoint.py`).
- `LICENSE` — MIT, copyright line exactly
  `Copyright (c) 2026 Asdale Dynamics, LLC`.
- `README.md` — install, usage, configuration, testing, credit to Asdale
  Dynamics, LLC, license. No `.github/workflows` files.

## How to run

```bash
cd etsy-listing-drafter-cli
python3 -m venv .venv
.venv/bin/pip install -e .          # or: PYTHONPATH=src python3 -m etsy_drafter
.venv/bin/pip install pytest        # for tests

# Start Ollama (default endpoint), then:
.venv/bin/etsy-drafter draft --details "A cream hand-knit wool scarf, 60 inches long."
.venv/bin/etsy-drafter list
.venv/bin/etsy-drafter export --out etsy-listings.csv

# Or override endpoint/model:
ETSY_DRAFTER_BASE_URL=http://localhost:11434/v1 ETSY_DRAFTER_MODEL=llama3.2 .venv/bin/etsy-drafter draft --details "..."
```

## Verification results

- `pytest`: 23 passed, including the mock OpenAI-compatible endpoint
  integration test (no real model or network required).
- `pip wheel .`: builds cleanly (`etsy_listing_drafter-0.1.0-py3-none-any.whl`).
- CLI smoke test against a live mock endpoint: `draft` → saved draft with
  title/description/tags; `list` shows it; `export --out` writes valid CSV.
- Unreachable endpoint → clear error message, exit code 1.
- Git initialized; initial commit `af8c3cb` "Initial commit: Etsy listing
  drafter CLI" (17 files), existing identity only, no co-author trailers,
  nothing pushed.

## Known gaps

- Requires a running local model (Ollama default); no bundled model and no
  cloud fallback by design (local-first).
- Interactive `draft` reads from stdin; not suited to non-TTY automation
  without `--details` / `--details-file`.
- JSON storage is a single file with no file locking; single-writer use only.
- Tags are taken as-is from the model (no deduplication beyond the prompt).
- No PyPI publication; intended to be installed from source (`pip install -e .`).
