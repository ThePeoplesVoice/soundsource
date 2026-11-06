#!/usr/bin/env python3
"""
SoundSource Management Engine Prototype
Grounded in universal principles. Ready for testing.
"""

import json
import csv
from datetime import date
from pathlib import Path

BASE = Path(__file__).parent.parent
LEDGER = BASE / "ledger" / "sample_ledger.csv"
SOURCES = BASE / "sources" / "real_yield_sources.json"

def load_ledger():
    rows = []
    with open(LEDGER, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def load_sources():
    with open(SOURCES) as f:
        return json.load(f)

def score_source(source, user_risk_tolerance=0.5):
    """Simple scoring. Higher is better for allocation preference."""
    sust = float(source["sustainability_score"])
    risk = float(source["risk_score"])
    align = float(source["alignment_score"])
    # Penalize high risk relative to tolerance
    risk_penalty = max(0, risk - user_risk_tolerance) * 0.5
    composite = (sust * 0.45 + align * 0.35 + (1 - risk) * 0.20) - risk_penalty
    return max(0.0, min(1.0, composite))

def suggest_allocation(sources, user_risk_tolerance=0.5, max_single=0.35):
    scored = []
    for s in sources:
        if s.get("emissions_dependent") and s["sustainability_score"] < 0.4:
            continue  # Principle filter
        score = score_source(s, user_risk_tolerance)
        scored.append((s, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    total_score = sum(sc for _, sc in scored) or 1
    allocation = []
    for s, sc in scored:
        weight = min(max_single, sc / total_score)
        allocation.append({
            "id": s["id"],
            "name": s["name"],
            "weight": round(weight, 3),
            "score": round(sc, 3),
            "category": s["category"]
        })
    # Normalize
    total_w = sum(a["weight"] for a in allocation) or 1
    for a in allocation:
        a["weight"] = round(a["weight"] / total_w, 3)
    return allocation

def detect_opportunities(sources):
    opps = []
    for s in sources:
        if s["sustainability_score"] >= 0.75 and s["risk_score"] <= 0.5:
            opps.append(f"{s['name']} — high sustainability, contained risk")
    return opps

def main():
    print("=" * 60)
    print("SoundSource Management Report")
    print(f"Generated: {date.today().isoformat()}")
    print("Principles: Sound Value | Sourced Transparency | Alignment")
    print("=" * 60)

    ledger = load_ledger()
    sources = load_sources()

    print(f"\nLedger rows loaded: {len(ledger)}")
    print(f"Source definitions: {len(sources)}")

    allocation = suggest_allocation(sources, user_risk_tolerance=0.45)
    print("\nSuggested Allocation (risk tolerance 0.45):")
    for a in allocation:
        print(f"  {a['weight']*100:5.1f}%  {a['name']}  (score {a['score']})")

    opps = detect_opportunities(sources)
    print("\nPrinciple-aligned Opportunities:")
    for o in opps:
        print(f"  • {o}")

    print("\nDrift / Notes from Ledger:")
    for row in ledger:
        if "medium" in row.get("confidence", "") or "low" in row.get("confidence", ""):
            print(f"  • {row['metric']}: confidence={row['confidence']} — verify primary source")

    print("\n" + "=" * 60)
    print("Test complete. Modify sample data and re-run to explore scenarios.")
    print("No capital is at risk in this prototype.")

if __name__ == "__main__":
    main()
