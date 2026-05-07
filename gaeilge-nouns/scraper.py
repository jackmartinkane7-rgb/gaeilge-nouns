"""
One-time setup script: scrapes Teanglann.ie for Irish noun forms and saves to nouns.json.
Run: python scraper.py
"""

import json
import re
import time
import sys
import requests
import urllib3
from bs4 import BeautifulSoup
from nouns_list import NOUNS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "https://www.teanglann.ie/en/gram/{}"
OUTPUT_FILE = "nouns.json"
DELAY = 1.0  # seconds between requests


def scrape_noun(word):
    url = BASE_URL.format(word)
    try:
        resp = requests.get(url, timeout=10, verify=False)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  ERROR fetching {word}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    result = {
        "word": word,
        "nom_sg": None, "nom_sg_article": None,
        "nom_pl": None, "nom_pl_article": None,
        "gen_sg": None, "gen_sg_article": None,
        "gen_pl": None, "gen_pl_article": None,
        "gender": None,
        "declension": None,
    }

    # The grammar block lives in div.dir.obverse.exacts > div.gram
    # (there is also a copy inside div.inside.gram used by the wizard — same structure)
    gram_div = soup.select_one("div.dir.obverse div.gram")
    if not gram_div:
        # fallback: first div.gram on page
        gram_div = soup.select_one("div.gram")
    if not gram_div:
        return result

    # Skip if Teanglann resolved the word as a verb, not a noun
    header = gram_div.select_one("div.header")
    if header:
        header_text = header.get_text(" ", strip=True).upper()
        if "VERB" in header_text and "NOUN" not in header_text:
            print(f"  SKIP: {word} resolved as VERB on Teanglann")
            return result

    # Gender and declension from div.property > div.value
    for prop in gram_div.select("div.property div.value"):
        text = prop.get_text(strip=True).upper()
        if text in ("MASCULINE", "FEMININE"):
            result["gender"] = text.capitalize()
        m = re.match(r'(\d+)(?:ST|ND|RD|TH) DECLENSION', text)
        if m:
            result["declension"] = int(m.group(1))

    # Navigate sections: Singular / Plural
    content = gram_div.select_one("div.content")
    if not content:
        return result

    for section in content.select("div.section"):
        # Determine if Singular or Plural from the section's first text node
        section_text = section.get_text(" ", strip=True)
        is_singular = section_text.upper().startswith("SINGULAR")
        is_plural = section_text.upper().startswith("PLURAL")

        for subsection in section.select("div.subsection"):
            sub_text = subsection.get_text(" ", strip=True).upper()
            is_nominative = sub_text.startswith("NOMINATIVE")
            is_genitive = sub_text.startswith("GENITIVE")

            # bare form: span.value.primary
            bare_el = subsection.select_one("span.value.primary")
            bare = bare_el.get_text(strip=True) if bare_el else None

            # article form: span.value inside div.line.bulletted
            art_el = subsection.select_one("div.line.bulletted span.value")
            article = art_el.get_text(strip=True) if art_el else None

            if is_singular and is_nominative:
                result["nom_sg"] = bare
                result["nom_sg_article"] = article
            elif is_singular and is_genitive:
                result["gen_sg"] = bare
                result["gen_sg_article"] = article
            elif is_plural and is_nominative:
                result["nom_pl"] = bare
                result["nom_pl_article"] = article
            elif is_plural and is_genitive:
                result["gen_pl"] = bare
                result["gen_pl_article"] = article

    return result


def main():
    existing = {}
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            existing = {entry["word"]: entry for entry in data}
        print(f"Loaded {len(existing)} existing entries from {OUTPUT_FILE}")
    except FileNotFoundError:
        print("No existing data file found, starting fresh.")

    results = list(existing.values())
    already_done = set(existing.keys())

    to_fetch = [w for w in NOUNS if w not in already_done]
    print(f"Fetching {len(to_fetch)} nouns (skipping {len(already_done)} already done)...\n")

    for i, noun in enumerate(to_fetch, 1):
        print(f"[{i:3}/{len(to_fetch)}] {noun:<20}", end=" ", flush=True)
        entry = scrape_noun(noun)
        if entry and entry["nom_sg"]:
            results.append(entry)
            print(f"ok  ({entry.get('gender','?')}, {entry.get('declension','?')} decl)  "
                  f"nom_sg={entry['nom_sg_article']}  gen_sg={entry['gen_sg_article']}")
        elif entry:
            results.append(entry)
            print("WARNING: no forms found")
        else:
            print("FAILED")
        time.sleep(DELAY)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    ok = sum(1 for r in results if r.get("nom_sg"))
    print(f"\nDone. {ok}/{len(results)} entries have noun forms.")
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
