#!/usr/bin/env python3
"""
SoundSource Unified Engine — Revolutionary Financial Provider
Combines real-yield source management with personal income allocation.
Grounded in universal principles. Ready for testing.
"""

import json
import csv
from datetime import date
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional

# Sample sources embedded for standalone testing; production loads from sources/
SAMPLE_SOURCES = [
    {
        "id": "aave-lending",
        "name": "Aave Lending Spread",
        "category": "Lending Spread",
        "real_yield_source": "Borrower interest paid to suppliers",
        "sustainability_score": 0.85,
        "risk_score": 0.35,
        "alignment_score": 0.70,
        "typical_apy_range": [0.03, 0.08],
        "emissions_dependent": False,
        "notes": "Mature protocol, real revenue from utilization."
    },
    {
        "id": "hyperliquid-fees",
        "name": "Hyperliquid Trading Fees",
        "category": "Trading Fees",
        "real_yield_source": "Perpetual trading fees shared with liquidity / protocol",
        "sustainability_score": 0.90,
        "risk_score": 0.45,
        "alignment_score": 0.75,
        "typical_apy_range": [0.05, 0.15],
        "emissions_dependent": False,
        "notes": "Strong real revenue. Newer, higher operational complexity."
    },
    {
        "id": "sky-rwa",
        "name": "Sky / Maker RWA + Stability",
        "category": "RWA Yield",
        "real_yield_source": "Stability fees + RWA yields on DAI/USDS",
        "sustainability_score": 0.80,
        "risk_score": 0.40,
        "alignment_score": 0.65,
        "typical_apy_range": [0.03, 0.06],
        "emissions_dependent": False,
        "notes": "Governance risk and RWA legal exposure. Real yield demonstrated."
    },
    {
        "id": "eth-staking",
        "name": "ETH Liquid Staking",
        "category": "Staking",
        "real_yield_source": "Network issuance + tips for security",
        "sustainability_score": 0.75,
        "risk_score": 0.30,
        "alignment_score": 0.60,
        "typical_apy_range": [0.02, 0.04],
        "emissions_dependent": True,
        "notes": "Issuance is protocol-defined. Slashing and LST discount risks."
    },
    {
        "id": "emissions-farm",
        "name": "Example Emissions Farm",
        "category": "Trading Fees",
        "real_yield_source": "Mostly new token emissions",
        "sustainability_score": 0.15,
        "risk_score": 0.70,
        "alignment_score": 0.20,
        "typical_apy_range": [0.20, 0.80],
        "emissions_dependent": True,
        "notes": "Filtered by principle. High headline APY, low sustainability."
    }
]

@dataclass
class IncomeStream:
    name: str
    monthly: float
    reliability: str
    type: str

def score_source(source: Dict, user_risk_tolerance: float = 0.5) -> float:
    sust = float(source["sustainability_score"])
    risk = float(source["risk_score"])
    align = float(source["alignment_score"])
    risk_penalty = max(0, risk - user_risk_tolerance) * 0.5
    composite = (sust * 0.45 + align * 0.35 + (1 - risk) * 0.20) - risk_penalty
    return max(0.0, min(1.0, composite))

def suggest_yield_allocation(sources: List[Dict], user_risk_tolerance: float = 0.45, max_single: float = 0.35) -> List[Dict]:
    scored = []
    for s in sources:
        if s.get("emissions_dependent") and s["sustainability_score"] < 0.4:
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
            "category": s["category"]
        })
    total_w = sum(a["weight"] for a in allocation) or 1
    for a in allocation:
        a["weight"] = round(a["weight"] / total_w, 3)
    return allocation

def allocate_personal(
    total_monthly_income: float,
    essential_expenses: float,
    emergency_current: float,
    emergency_target: float,
    high_interest_debt: float,
    invest_rate: float = 0.15,
) -> Dict:
    notes = []
    net = total_monthly_income - essential_expenses
    if net <= 0:
        notes.append("ALERT: Expenses >= income. Prioritize reduction or new income. No discretionary.")
        return {"emergency": 0, "debt": 0, "invest": 0, "goals": 0, "discretionary": max(0, net), "notes": notes}

    remaining = net
    emergency_gap = max(0, emergency_target - emergency_current)
    emergency_alloc = min(remaining * 0.5, emergency_gap)
    remaining -= emergency_alloc
    if emergency_alloc > 0:
        notes.append(f"Emergency fill: {emergency_alloc:.2f} toward gap of {emergency_gap:.2f}")

    debt_alloc = 0.0
    if high_interest_debt > 0 and remaining > 0:
        debt_alloc = min(remaining * 0.3, high_interest_debt)
        remaining -= debt_alloc
        notes.append(f"High-interest debt: {debt_alloc:.2f}")

    invest_alloc = remaining * invest_rate if remaining > 0 else 0
    remaining -= invest_alloc
    if invest_alloc > 0:
        notes.append(f"Investment (pay yourself first): {invest_alloc:.2f}")

    goals_alloc = remaining * 0.3 if remaining > 0 else 0
    remaining -= goals_alloc
    discretionary = remaining
    notes.append(f"Discretionary after rules: {discretionary:.2f}")

    return {
        "emergency": emergency_alloc,
        "debt": debt_alloc,
        "invest": invest_alloc,
        "goals": goals_alloc,
        "discretionary": discretionary,
        "notes": notes
    }

def project(monthly_invest: float, years: int, annual_return: float = 0.06, current_pv: float = 0) -> float:
    if monthly_invest <= 0 and current_pv <= 0:
        return 0.0
    r = annual_return / 12
    n = years * 12
    fv_pv = current_pv * (1 + r) ** n
    if r == 0:
        fv_pmt = monthly_invest * n
    else:
        fv_pmt = monthly_invest * (((1 + r) ** n - 1) / r)
    return fv_pv + fv_pmt

def main():
    print("=" * 70)
    print("SoundSource Unified Management Report")
    print(f"Generated: {date.today().isoformat()}")
    print("Principles: Sound Value | Sourced Transparency | Incentive Alignment |")
    print("           Spend < Earn | Pay Yourself First | Adaptive Resilience")
    print("=" * 70)

    streams = [
        IncomeStream("Primary job", 4500.0, "high", "primary"),
        IncomeStream("Side freelance", 600.0, "medium", "secondary"),
        IncomeStream("Investment income", 50.0, "low", "passive"),
    ]
    total_income = sum(s.monthly for s in streams)
    essential = 2800.0
    emergency_current = 0.0
    emergency_target = essential * 4
    high_interest_debt = 0.0

    print("\n--- Personal Income Streams ---")
    for s in streams:
        print(f"  {s.name:20} {s.monthly:8.2f}  ({s.reliability}, {s.type})")
    print(f"Total monthly income: {total_income:.2f}")
    print(f"Essential expenses:   {essential:.2f}")
    print(f"Net before allocation:{total_income - essential:.2f}")

    personal = allocate_personal(total_income, essential, emergency_current, emergency_target, high_interest_debt)
    print("\n--- Personal Allocation (Pay Yourself First) ---")
    print(f"  Emergency:     {personal['emergency']:.2f}")
    print(f"  Debt:          {personal['debt']:.2f}")
    print(f"  Invest:        {personal['invest']:.2f}")
    print(f"  Goals:         {personal['goals']:.2f}")
    print(f"  Discretionary: {personal['discretionary']:.2f}")
    print("Notes:")
    for n in personal["notes"]:
        print(f"  - {n}")

    print("\n--- Projections on Invest Stream @ 6% ---")
    for years in [5, 10, 20]:
        fv = project(personal["invest"], years)
        print(f"  {years:2d} years: {fv:,.0f}")

    print("\n--- Real-Yield Source Allocation (for invest capital) ---")
    yield_alloc = suggest_yield_allocation(SAMPLE_SOURCES, user_risk_tolerance=0.45)
    for a in yield_alloc:
        print(f"  {a['weight']*100:5.1f}%  {a['name']}  (score {a['score']})")

    print("\n--- Principle-aligned Opportunities ---")
    for s in SAMPLE_SOURCES:
        if s["sustainability_score"] >= 0.75 and s["risk_score"] <= 0.5:
            print(f"  • {s['name']} — high sustainability, contained risk")

    print("\n" + "=" * 70)
    print("Test complete. Edit sample streams/expenses or sources and re-run.")
    print("No capital is at risk in this prototype. Ready for your real numbers.")
    print("Current Finary state: €0 net worth — ideal clean slate.")

if __name__ == "__main__":
    main()
