#!/usr/bin/env python3
"""
SoundSource Management Engine v0.2
Grounded in universal principles. Enhanced for testing readiness.
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
    sust = float(source["sustainability_score"])
    risk = float(source["risk_score"])
    align = float(source["alignment_score"])
    risk_penalty = max(0, risk - user_risk_tolerance) * 0.5
    composite = (sust * 0.45 + align * 0.35 + (1 - risk) * 0.20) - risk_penalty
    return max(0.0, min(1.0, composite))

def suggest_allocation(sources, user_risk_tolerance=0.5, max_single=0.35):
    scored = []
    for s in sources:
        if s.get("emissions_dependent") and float(s["sustainability_score"]) < 0.4:
            continue
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
            "category": s["category"],
            "notes": s.get("notes", "")
        })
    total_w = sum(a["weight"] for a in allocation) or 1
    for a in allocation:
        a["weight"] = round(a["weight"] / total_w, 3)
    return allocation

def detect_opportunities(sources):
    return [
        f"{s['name']} — high sustainability ({s['sustainability_score']}), contained risk ({s['risk_score']})"
        for s in sources
        if float(s["sustainability_score"]) >= 0.75 and float(s["risk_score"]) <= 0.5
    ]

def principles_check(sources, allocation):
    checks = []
    filtered = [s["name"] for s in sources if s.get("emissions_dependent") and float(s["sustainability_score"]) < 0.4]
    checks.append(f"Sound Value filter applied: excluded {len(filtered)} emissions-dependent low-sustainability source(s)")
    total_w = sum(a["weight"] for a in allocation)
    checks.append(f"Allocation integrity: weights sum to {total_w:.3f} (target 1.0)")
    checks.append("Sourced Transparency: ledger confidence notes surface medium/low items")
    checks.append("Incentive Alignment: scores weight long-term alignment (0.35 factor)")
    return checks

def generate_report(allocation, opps, ledger, checks, risk_tol=0.45):
    lines = [
        "# SoundSource Management Report",
        f"**Generated:** {date.today().isoformat()}",
        "**Principles:** Sound Value | Sourced Transparency | Incentive Alignment | Risk Isolation | Optionality | Adaptive Resilience",
        "",
        f"**User risk tolerance:** {risk_tol}",
        "",
        "## Suggested Allocation",
        "",
        "| Weight | Name | Score | Category |",
        "|--------|------|-------|----------|"
    ]
    for a in allocation:
        lines.append(f"| {a['weight']*100:.1f}% | {a['name']} | {a['score']} | {a['category']} |")
    lines += [
        "",
        "## Principle-aligned Opportunities",
        ""
    ]
    for o in opps:
        lines.append(f"- {o}")
    lines += [
        "",
        "## Principles Check",
        ""
    ]
    for c in checks:
        lines.append(f"- {c}")
    lines += [
        "",
        "## Ledger Drift / Confidence Notes",
        ""
    ]
    for row in ledger:
        conf = row.get("confidence", "")
        if "medium" in conf or "low" in conf:
            lines.append(f"- {row['metric']}: confidence={conf} — verify primary source ({row.get('source','')})")
    lines += [
        "",
        "---",
        "*Prototype only. No capital at risk. Test edge cases by editing sources and ledger.*"
    ]
    return "\n".join(lines)

def main():
    print("=" * 60)
    print("SoundSource Management Report v0.2")
    print(f"Generated: {date.today().isoformat()}")
    print("=" * 60)

    ledger = load_ledger()
    sources = load_sources()

    print(f"\nLedger rows: {len(ledger)} | Sources: {len(sources)}")

    allocation = suggest_allocation(sources, user_risk_tolerance=0.45)
    print("\nSuggested Allocation:")
    for a in allocation:
        print(f"  {a['weight']*100:5.1f}%  {a['name']}  (score {a['score']})")

    opps = detect_opportunities(sources)
    print("\nOpportunities:")
    for o in opps:
        print(f"  • {o}")

    checks = principles_check(sources, allocation)
    print("\nPrinciples Check:")
    for c in checks:
        print(f"  • {c}")

    report = generate_report(allocation, opps, ledger, checks)
    report_path = BASE / "tests" / "latest_report.md"
    report_path.write_text(report)
    print(f"\nFull report written to: {report_path}")

    print("\n" + "=" * 60)
    print("v0.2 test complete. Ready for further testing.")

if __name__ == "__main__":
    main()
