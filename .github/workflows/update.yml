"""
Scraper des résultats du Loto 5/90 (lnbloto.bj/results).

Stratégie : plutôt que de dépendre de sélecteurs CSS fragiles (qui cassent
dès que le site change son design), on lit le TEXTE structuré de la page
et on le parse avec une regex. Le format observé est stable :

    Digital 00H
    18 septembre 2026
    13   33   23   72   46

Si le site change complètement sa structure de texte, cette regex devra
être ajustée (c'est le point le plus probable de maintenance future).
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "https://lnbloto.bj/results"
DATA_FILE = Path(__file__).parent.parent / "data" / "tirages.json"

MOIS = {
    "janvier": "01", "février": "02", "mars": "03", "avril": "04",
    "mai": "05", "juin": "06", "juillet": "07", "août": "08",
    "septembre": "09", "octobre": "10", "novembre": "11", "décembre": "12",
}

# Capture : nom du tirage (ex: "Digital 00H"), date en toutes lettres,
# puis 5 nombres (les numéros gagnants).
PATTERN = re.compile(
    r"(Digital|Fortune|Star)\s+(\d{1,2}H)\s*\n"
    r"\s*(\d{1,2})\s+(" + "|".join(MOIS.keys()) + r")\s+(\d{4})\s*\n"
    r"\s*(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})",
    re.IGNORECASE,
)


def scrape() -> list[dict]:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 420, "height": 1200})
        page.goto(URL, wait_until="networkidle", timeout=30000)
        # Laisse le temps au JS de peupler la liste de résultats
        page.wait_for_timeout(2000)
        text = page.inner_text("body")
        browser.close()

    draws = []
    for m in PATTERN.finditer(text):
        type_, heure, jour, mois_nom, annee, n1, n2, n3, n4, n5 = m.groups()
        mois = MOIS[mois_nom.lower()]
        date_iso = f"{annee}-{mois}-{int(jour):02d}"
        draws.append({
            "date": date_iso,
            "heure": heure.upper(),
            "type": type_,
            "numeros": sorted(int(x) for x in (n1, n2, n3, n4, n5)),
        })
    return draws


def merge_and_save(new_draws: list[dict]) -> int:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if DATA_FILE.exists():
        existing = json.loads(DATA_FILE.read_text())

    seen = {(d["date"], d["heure"]) for d in existing}
    added = 0
    for d in new_draws:
        key = (d["date"], d["heure"])
        if key not in seen:
            existing.append(d)
            seen.add(key)
            added += 1

    heure_order = {"00H": 0, "08H": 1, "11H": 2, "14H": 3, "18H": 4, "20H": 5}
    existing.sort(key=lambda d: (d["date"], heure_order.get(d["heure"], 9)))

    DATA_FILE.write_text(json.dumps(existing, indent=2, ensure_ascii=False))
    return added


if __name__ == "__main__":
    print(f"[{datetime.now().isoformat()}] Scraping {URL} ...")
    try:
        found = scrape()
    except Exception as e:
        print(f"ERREUR pendant le scraping : {e}", file=sys.stderr)
        sys.exit(1)

    if not found:
        print("Aucun tirage trouvé — la regex ne correspond probablement plus "
              "à la structure du site. Vérifier manuellement lnbloto.bj/results.")
        sys.exit(1)

    added = merge_and_save(found)
    print(f"{len(found)} tirages lus sur la page, {added} nouveaux ajoutés à la base.")

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"added={added}\n")
