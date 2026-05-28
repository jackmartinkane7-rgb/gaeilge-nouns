# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A two-stage Irish (Gaeilge) noun declension practice tool:

1. **Scraper** (`scraper.py`) — one-time setup that fetches noun forms from teanglann.ie and writes `nouns.json`
2. **App** (`app.py`) — tkinter GUI that loads `nouns.json` and quizzes the user on all four declension forms (nominative/genitive × singular/plural) plus their article forms

## Setup and running

```bash
pip install -r requirements.txt   # requests, beautifulsoup4

python scraper.py                  # one-time: creates/updates nouns.json
python app.py                      # launch the practice GUI
```

`nouns.json` must exist before `app.py` will start. The scraper is incremental — re-running it skips words already in `nouns.json`.

## Testing

```bash
python test_scraper.py             # live scrape of a handful of nouns, prints results to stdout
```

There are no unit tests; `test_scraper.py` makes real HTTP requests to teanglann.ie.

## Data flow

`nouns_list.py` (source list of ~250 Irish nouns)
→ `scraper.py` fetches each word from `https://www.teanglann.ie/en/gram/{word}`
→ `nouns.json` (cached data, one object per noun)
→ `app.py` reads and quizzes

Each entry in `nouns.json` has: `word`, `gender`, `declension`, and eight form fields: `nom_sg`, `nom_sg_article`, `nom_pl`, `nom_pl_article`, `gen_sg`, `gen_sg_article`, `gen_pl`, `gen_pl_article`.

The app checks article forms (e.g. `"an chistin"`) — **not** the bare forms — and distinguishes exact matches from accent errors (fadas).

## Scraper notes

- SSL verification is disabled (`verify=False`) because teanglann.ie has certificate issues; `urllib3` warnings are suppressed at import time.
- A 1-second delay (`DELAY = 1.0`) is applied between requests to avoid hammering the server.
- Words that teanglann.ie resolves as verbs (not nouns) are skipped automatically.
- The HTML target is `div.dir.obverse div.gram` with subsections for Singular/Plural → Nominative/Genitive.
