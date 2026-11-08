#!/usr/bin/env python3
"""
SoundSource Management Engine — Enhanced Prototype
Grounded in universal principles. Ready for local testing.
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

def score_source(source, user_risk_tolerance=0.45):
    """Composite score. Higher = preferred under principles."""
    sust = float(source.get("sustainability_score", 0))
    risk = float(source.get("risk_score", 1))
    align = float(source.get("alignment_score", 0))

    # Principle filter already applied upstream for emissions
    risk_penalty = max(0.0, risk - user_risk_tolerance) * 0.6
    composite = (sust * 0.50 + align * 0.30 + (1 - risk) * 0.20) - risk_penalty
    return max(0.0, min(1.0, composite))

def suggest_allocation(sources, user_risk_tolerance=0.45, max_single=0.40):
    scored = []
    for s in sources:
        # Hard filter: emissions-dependent + low sustainability
        if s.get("emissions_dependent") and float(s.get("sustainability_score", 0)) < 0.45:
            continue
        score = score_source(s, user_risk_tolerance)
        if score < 0.15:  # too weak under principles
            continue
        scored.append((s, score))

    if not scored:
        return []

    scored.sort(key=lambda x: x[1], reverse=True)
    total_score = sum(sc for _, sc in scored) or 1.0

    allocation = []
    for s, sc in scored:
        weight = min(max_single, sc / total_score)
        allocation.append({
            "id": s["id"],
            "name": s["name"],
            "category": s["category"],
            "weight": weight,
            "score": round(sc, 3),
            "sustainability": s.get("sustainability_score"),
            "risk": s.get("risk_score"),
            "notes": s.get("notes", "")
        })

    # Normalize weights to sum to 1.0
    total_w = sum(a["weight"] for a in allocation) or 1.0
    for a in allocation:
        a["weight"] = round(a["weight"] / total_w, 4)

    return allocation

def detect_opportunities(sources):
    opps = []
    for s in sources:
        sust = float(s.get("sustainability_score", 0))
        risk = float(s.get("risk_score", 1))
        if sust >= 0.75 and risk <= 0.50 and not (s.get("emissions_dependent") and sust < 0.6):
            opps.append({
                "name": s["name"],
                "reason": "High sustainability with contained risk",
                "score_hint": round(sust * 0.6 + (1 - risk) * 0.4, 2)
            })
    return opps

def generate_report(user_risk_tolerance=0.45):
    ledger = load_ledger()
    sources = load_sources()
    allocation = suggest_allocation(sources, user_risk_tolerance)
    opps = detect_opportunities(sources)

    lines = []
    lines.append("# SoundSource Management Report")
    lines.append(f"**Generated:** {date.today().isoformat()}")
    lines.append("**Principles:** Sound Value · Sourced Transparency · Incentive Alignment · Risk Isolation · Optionality · Adaptive Resilience")
    lines.append("")
    lines.append(f"Ledger rows: {len(ledger)} | Source definitions: {len(sources)} | Risk tolerance: {user_risk_tolerance}")
    lines.append("")

    if not allocation:
        lines.append("**No sources passed the principle filter at this risk tolerance.**")
        lines.append("Consider raising tolerance slightly or reviewing source scores.")
    else:
        lines.append("## Suggested Allocation")
        lines.append("")
        lines.append("| Weight | Source | Score | Category |")
        lines.append("|--------|--------|-------|----------|")
        for a in allocation:
            lines.append(f"| {a['weight']*100:.1f}% | {a['name']} | {a['score']} | {a['category']} |")
        lines.append("")

    if opps:
        lines.append("## Principle-Aligned Opportunities")
        for o in opps:
            lines.append(f"- **{o['name']}** — {o['reason']} (hint {o['score_hint']})")
        lines.append("")

    lines.append("## Ledger Drift / Confidence Notes")
    low_conf = [r for r in ledger if r.get("confidence", "").lower() in ("medium", "low")]
    if low_conf:
        for row in low_conf:
            lines.append(f"- {row.get('metric')}: confidence={row.get('confidence')} — verify primary source ({row.get('source')})")
    else:
        lines.append("- All loaded rows carry high confidence in this sample.")
    lines.append("")

    lines.append("---")
    lines.append("*Prototype. No capital at risk. Test with real sourced rows before any live use.*")

    return "\n".join(lines)

def main():
    report = generate_report(user_risk_tolerance=0.45)
    print(report)

    # Also write a dated markdown for artifacts
    out = BASE / "tests" / f"report-{date.today().isoformat()}.md"
    out.write_text(report)
    print(f"\nReport written to {out}")

if __name__ == "__main__":
    main()
