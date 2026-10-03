"""
Calcule les tendances à partir de data/tirages.json :
- numéros "à surveiller" (basé sur l'historique des numéros qui suivent
  les numéros du dernier tirage, + boost des numéros doubles)
- numéros en retard (écarts)
- duos / trios historiquement fréquents (2 Nap / 3 Nap)

Sortie : data/tendances.json, consommé par generate_site.py et
telegram_post.py.
"""

import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "tirages.json"
OUT_FILE = Path(__file__).parent.parent / "data" / "tendances.json"

DOUBLES = {11, 22, 33, 44, 55, 66, 77, 88}
DOUBLE_BOOST = 3  # poids ajouté par double présent dans le dernier tirage


def load_draws():
    raw = json.loads(DATA_FILE.read_text())
    return [sorted(d["numeros"]) for d in raw], raw


def analyze():
    draws, raw = load_draws()
    total = len(draws)
    if total < 2:
        raise SystemExit("Pas assez de tirages pour calculer des tendances (minimum 2).")

    # --- Fréquence globale ---
    freq = Counter()
    for d in draws:
        freq.update(d)

    # --- Écarts (tirages depuis la dernière sortie) ---
    last_seen = {}
    for idx, d in enumerate(draws):
        for n in d:
            last_seen[n] = idx
    ecarts = {n: total - 1 - last_seen.get(n, -1) for n in range(1, 91)}

    # --- Suivi numéro -> numéro (tirage i -> tirage i+1) ---
    follow_counts = defaultdict(Counter)
    for i in range(total - 1):
        for x in draws[i]:
            for y in draws[i + 1]:
                follow_counts[x][y] += 1

    # --- Duos / trios historiques ---
    pair_freq, trip_freq = Counter(), Counter()
    for d in draws:
        for c in combinations(d, 2):
            pair_freq[c] += 1
        for c in combinations(d, 3):
            trip_freq[c] += 1

    # --- Tendance pour le prochain tirage ---
    last_draw = draws[-1]
    last_draw_meta = raw[-1]
    combined = Counter()
    for x in last_draw:
        for y, c in follow_counts[x].items():
            combined[y] += c

    # Règle des doubles : si le dernier tirage contient un double,
    # on booste le score des AUTRES doubles.
    doubles_in_last = [n for n in last_draw if n in DOUBLES]
    if doubles_in_last:
        for d in DOUBLES - set(doubles_in_last):
            combined[d] += DOUBLE_BOOST

    tendance = [n for n, _ in combined.most_common(5)]

    result = {
        "total_tirages": total,
        "dernier_tirage": {
            "date": last_draw_meta["date"],
            "heure": last_draw_meta["heure"],
            "type": last_draw_meta.get("type", ""),
            "numeros": last_draw,
        },
        "doubles_actifs": doubles_in_last,
        "a_surveiller": tendance,
        "numeros_en_retard": [
            {"numero": n, "ecart": e}
            for n, e in sorted(ecarts.items(), key=lambda x: -x[1])[:5]
        ],
        "duos_frequents": [
            {"paire": list(p), "fois": c} for p, c in pair_freq.most_common(5)
        ],
        "trios_frequents": [
            {"trio": list(t), "fois": c} for t, c in trip_freq.most_common(5)
        ],
    }

    OUT_FILE.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    return result


if __name__ == "__main__":
    r = analyze()
    print(f"Tendances calculées sur {r['total_tirages']} tirages.")
    print(f"À surveiller : {r['a_surveiller']}")
    if r["doubles_actifs"]:
        print(f"Règle des doubles activée (doubles présents : {r['doubles_actifs']})")
