#!/usr/bin/env python3
"""
SoundSource Management Engine v2
Revolutionary Financial Provider — Income Sources & Management
Grounded in universal principles of sound value, sourced transparency,
incentive alignment, risk isolation, optionality, and adaptive resilience.

Ready for testing. No capital at risk in prototype.
"""

import json
import csv
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict, Any
import argparse

BASE = Path(__file__).parent.parent
LEDGER = BASE / "ledger" / "sample_ledger.csv"
SOURCES = BASE / "sources" / "real_yield_sources.json"

def load_ledger() -> List[Dict[str, str]]:
    if not LEDGER.exists():
        return []
    rows = []
    with open(LEDGER, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows

def load_sources() -> List[Dict[str, Any]]:
    if not SOURCES.exists():
        return []
    with open(SOURCES, encoding="utf-8") as f:
        return json.load(f)

def score_source(source: Dict[str, Any], user_risk_tolerance: float = 0.5) -> float:
    """
    Composite score 0-1. Higher better.
    Weights: sustainability 45%, alignment 35%, inverse risk 20%.
    Additional risk penalty if exceeds tolerance.
    """
    try:
        sust = float(source.get("sustainability_score", 0))
        risk = float(source.get("risk_score", 1))
        align = float(source.get("alignment_score", 0))
    except (TypeError, ValueError):
        return 0.0

    risk_penalty = max(0.0, risk - user_risk_tolerance) * 0.6
    composite = (sust * 0.45 + align * 0.35 + (1.0 - risk) * 0.20) - risk_penalty
    return max(0.0, min(1.0, composite))

def suggest_allocation(
    sources: List[Dict[str, Any]],
    user_risk_tolerance: float = 0.5,
    max_single: float = 0.35,
    min_score: float = 0.3
) -> List[Dict[str, Any]]:
    scored = []
    for s in sources:
        # Principle filter: reject pure emissions with low sustainability
        if s.get("emissions_dependent") and float(s.get("sustainability_score", 0)) < 0.45:
            continue
        score = score_source(s, user_risk_tolerance)
        if score < min_score:
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
            "id": s.get("id", "unknown"),
            "name": s.get("name", "Unknown"),
            "weight": weight,
            "score": round(sc, 3),
            "category": s.get("category", "Other"),
            "notes": s.get("notes", "")
        })

    # Normalize weights to sum to 1.0
    total_w = sum(a["weight"] for a in allocation) or 1.0
    for a in allocation:
        a["weight"] = round(a["weight"] / total_w, 4)

    return allocation

def detect_opportunities(sources: List[Dict[str, Any]]) -> List[str]:
    opps = []
    for s in sources:
        sust = float(s.get("sustainability_score", 0))
        risk = float(s.get("risk_score", 1))
        if sust >= 0.75 and risk <= 0.50:
            opps.append(
                f"{s.get('name')} — high sustainability ({sust:.2f}), contained risk ({risk:.2f})"
            )
    return opps

def analyze_ledger_drift(ledger: List[Dict[str, str]]) -> List[str]:
    notes = []
    for row in ledger:
        conf = str(row.get("confidence", "")).lower()
        if "medium" in conf or "low" in conf or "unknown" in conf:
            notes.append(
                f"{row.get('metric', 'Unknown')}: confidence={row.get('confidence')} "
                f"(as_of {row.get('as_of', '?')}) — verify primary source: {row.get('source', '')}"
            )
    return notes

def generate_report(
    user_risk_tolerance: float = 0.45,
    max_single: float = 0.35
) -> str:
    ledger = load_ledger()
    sources = load_sources()
    allocation = suggest_allocation(sources, user_risk_tolerance, max_single)
    opps = detect_opportunities(sources)
    drifts = analyze_ledger_drift(ledger)

    lines = [
        "=" * 70,
        "SoundSource Management Report v2",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} AWST",
        "Principles: Sound Value | Sourced Transparency | Incentive Alignment",
        "           Risk Isolation | Optionality | Adaptive Resilience",
        "=" * 70,
        f"\nLedger rows loaded: {len(ledger)}",
        f"Source definitions: {len(sources)}",
        f"User risk tolerance: {user_risk_tolerance:.2f} (0=conservative, 1=aggressive)",
        "",
        "Suggested Allocation:",
    ]

    if not allocation:
        lines.append("  No sources met principle and score thresholds.")
    else:
        for a in allocation:
            lines.append(
                f"  {a['weight']*100:6.1f}%  {a['name']:<35} (score {a['score']:.3f})  [{a['category']}]"
            )

    lines.append("\nPrinciple-aligned Opportunities:")
    if opps:
        for o in opps:
            lines.append(f"  • {o}")
    else:
        lines.append("  • None currently meet high-sustainability + contained-risk bar.")

    lines.append("\nDrift / Verification Notes from Ledger:")
    if drifts:
        for d in drifts:
            lines.append(f"  • {d}")
    else:
        lines.append("  • No low/medium confidence items flagged.")

    lines.extend([
        "",
        "=" * 70,
        "Test complete. Modify sample data or risk tolerance and re-run.",
        "No capital is at risk in this prototype. Always verify primary sources.",
        "SoundSource does not promise returns — it promises principle-aligned selection",
        "and full source transparency.",
        "=" * 70,
    ])
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="SoundSource Management Engine v2")
    parser.add_argument("--risk", type=float, default=0.45, help="Risk tolerance 0.0-1.0")
    parser.add_argument("--max-single", type=float, default=0.35, help="Max weight for single source")
    args = parser.parse_args()

    report = generate_report(args.risk, args.max_single)
    print(report)

    # Also write report to file for testing
    out_path = BASE / "tests" / f"report_{date.today().isoformat()}.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"\nReport written to: {out_path}")

if __name__ == "__main__":
    main()
