# Etsy Listing Drafter CLI

A warm, beginner-friendly Python CLI that drafts Etsy listing titles,
descriptions, and tags from your item details. It talks to a configurable
OpenAI-compatible endpoint — defaulting to Ollama on your own machine — so it
runs entirely locally with no API keys, no sign-ups, and no secrets.

Built by Dylan Asdale, registered nurse turned AI author and founder of
**Asdale Dynamics, LLC** (Indiana, formed October 2026). Plain English, step by
step, never condescending — AI explained "like a friend would." Part of the
LLC's open-source tools for resellers, authors, and small business owners.

## What it does

`etsy-drafter draft` takes a few sentences about your item and returns:

- A title (140 characters or fewer, keyword-forward, plain English)
- A warm, helpful description (what it is, what it's for, materials, how to use it — no medical claims, no promises of results)
- Exactly 13 tags (each 20 characters or fewer)

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

- Python 3.9+ (standard library only — no third-party packages required)
- An OpenAI-compatible chat endpoint. Default is Ollama at
  `http://localhost:11434/v1`

Start Ollama and pull a model:

```bash
ollama serve            # in one terminal
ollama pull llama3.2    # or any chat model you like
```

## Usage

### Draft a listing

Interactive mode (type your item details, press Enter on a blank line when done):

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

Example output:

```text
============================================================
Draft
============================================================
Title: Cream Wool Scarf - Hand Knit

Description:
Cozy cream hand-knit wool scarf.

Tags: wool scarf, hand knit, cream, handmade, etsy, gift, craft, ...
```

### List stored drafts

```bash
etsy-drafter list
```

### Export to CSV

```bash
etsy-drafter export --out etsy-listings.csv
```

Example `etsy-listings.csv`:

```csv
id,created_at,title,description,tags,item_details
680b33f3...,2026-11-02T14:00:21+00:00,Cream Wool Scarf - Hand Knit,Cozy cream hand-knit wool scarf.,wool scarf; hand knit; cream; handmade; etsy; gift; craft; unique; artisan; vintage; accessory; home; decor,"A cream hand-knit wool scarf, about 60 inches long."
```

Columns: `id`, `created_at`, `title`, `description`, `tags`, `item_details`.
Tags are joined with `; `.

### Configure endpoint, model, storage

| Option | Env var | Default | CLI flag |
|--------|---------|---------|----------|
| Endpoint base URL | `ETSY_DRAFTER_BASE_URL` | `http://localhost:11434/v1` | `--base-url` |
| Model | `ETSY_DRAFTER_MODEL` | `llama3.2` | `--model` |
| Timeout (seconds) | `ETSY_DRAFTER_TIMEOUT` | `60` | (draft only) |
| Storage path | `ETSY_DRAFTER_STORAGE` | `~/.etsy_drafter/listings.json` | `--storage` |

CLI flags override environment variables.

## Troubleshooting

**`Could not reach LLM endpoint at http://localhost:11434/v1`**

Make sure Ollama is running and a model is pulled:

```bash
ollama serve
ollama pull llama3.2
```

Or point the tool at another OpenAI-compatible endpoint:

```bash
etsy-drafter draft --details "..." \
  --base-url http://your-endpoint/v1 \
  --model your-model
```

**`LLM endpoint returned unexpected response shape`**

The model may not have returned JSON. The tool tries to repair imperfect JSON
and falls back gracefully, but results are best with a capable chat model.

**No drafts found**

Drafts are stored at `~/.etsy_drafter/listings.json` by default. Use
`--storage` or `ETSY_DRAFTER_STORAGE` to check a different location.

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
