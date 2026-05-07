"""Quick test: scrape a few nouns and print results."""
import sys
sys.stdout.reconfigure(encoding="utf-8")

from scraper import scrape_noun

for word in ["cistin", "fear", "bean", "abhainn", "lá"]:
    entry = scrape_noun(word)
    if entry:
        print(f"\n{word}")
        print(f"  Gender: {entry['gender']}  Declension: {entry['declension']}")
        print(f"  Nom Sg:  {entry['nom_sg']!r:20}  article: {entry['nom_sg_article']!r}")
        print(f"  Gen Sg:  {entry['gen_sg']!r:20}  article: {entry['gen_sg_article']!r}")
        print(f"  Nom Pl:  {entry['nom_pl']!r:20}  article: {entry['nom_pl_article']!r}")
        print(f"  Gen Pl:  {entry['gen_pl']!r:20}  article: {entry['gen_pl_article']!r}")
    else:
        print(f"\n{word}: FAILED")
