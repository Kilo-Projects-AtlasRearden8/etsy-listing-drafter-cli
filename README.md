# Etsy Listing Drafter CLI

A local-first Python CLI that drafts Etsy listing titles, descriptions, and tags
from your item details using a configurable OpenAI-compatible endpoint — defaulting
to Ollama, so it runs entirely on your machine with no API keys and no secrets.

Written in plain English, step by step, built by Dylan Asdale, founder of
**Asdale Dynamics, LLC** (Indiana, formed October 2026) — beginner-friendly AI
education, books, and practical tools.

## What it does

`etsy-drafter draft` takes a few sentences about your item and returns:

- A title (140 characters or fewer, keyword-forward)
- A warm, helpful description (what it is, what it's for, materials, how to use it)
- 13 tags (20 characters or fewer each)

Drafts are saved to a local JSON file and can be exported to CSV for your Etsy
shop workflow. Nothing leaves your machine unless you choose to point it at a
remote endpoint.

## Install

```bash
git clone <this-repo>
cd etsy-listing-drafter-cli
pip install -e .
```

Or run straight from source without installing:

```bash
PYTHONPATH=src python3 -m etsy_drafter --help
```

## Requirements

- Python 3.9+ (standard library only — no `pip install` needed beyond the package itself)
- An OpenAI-compatible chat endpoint. Default is Ollama at `http://localhost:11434/v1`

Start Ollama and pull a model:

```bash
ollama serve            # in one terminal
ollama pull llama3.2    # or any chat model you like
```

## Usage

### Draft a listing

Interactive mode (type your item details, blank line to finish):

```bash
etsy-drafter draft
```

Pass details directly:

```bash
etsy-drafter draft --details "A cream hand-knit wool scarf, about 60 inches long."
```

Read details from a file:

```bash
etsy-drafter draft --details-file notes.txt
```

Override the endpoint or model:

```bash
etsy-drafter draft --details "..." --base-url http://localhost:11434/v1 --model llama3.2
```

Environment variables work too:

```bash
export ETSY_DRAFTER_BASE_URL=http://localhost:11434/v1
export ETSY_DRAFTER_MODEL=llama3.2
export ETSY_DRAFTER_STORAGE=~/.etsy_drafter/listings.json
```

### List stored drafts

```bash
etsy-drafter list
```

### Export to CSV

```bash
etsy-drafter export --out etsy-listings.csv
```

Columns: `id, created_at, title, description, tags, item_details`. Tags are
joined with `; `.

## Configuration

| Option | Env var | Default |
|--------|---------|---------|
| Endpoint base URL | `ETSY_DRAFTER_BASE_URL` | `http://localhost:11434/v1` |
| Model | `ETSY_DRAFTER_MODEL` | `llama3.2` |
| Timeout (seconds) | `ETSY_DRAFTER_TIMEOUT` | `60` |
| Storage path | `ETSY_DRAFTER_STORAGE` | `~/.etsy_drafter/listings.json` |

CLI flags (`--base-url`, `--model`, `--storage`) override environment variables.

## Testing

```bash
pip install pytest
pytest
```

The suite includes a mock OpenAI-compatible HTTP endpoint test that exercises
the client end to end with no real model or network required.

## Credit

Built by Dylan Asdale, registered nurse turned AI author and founder of
**Asdale Dynamics, LLC**. Plain English, step by step, never condescending —
AI explained "like a friend would." Learn more at dylanasdale.github.io and
in *The Massive AI Manual*.

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.
