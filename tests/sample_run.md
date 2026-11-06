# SoundSource — Sample Test Run

Run date: 2026-11-06  
Command: `python engine/soundsource.py`

## Expected Output Shape

```
============================================================
SoundSource Management Report
Generated: 2026-11-06
Principles: Sound Value | Sourced Transparency | Alignment
============================================================

Ledger rows loaded: 9
Source definitions: 5

Suggested Allocation (risk tolerance 0.45):
   xx.x%  Hyperliquid Trading Fees  (score x.xxx)
   xx.x%  Aave Lending Spread       (score x.xxx)
   ...

Principle-aligned Opportunities:
  • Hyperliquid Trading Fees — high sustainability, contained risk
  • ...

Drift / Notes from Ledger:
  • ... confidence=medium — verify primary source

============================================================
Test complete. ...
```

## How to Test

1. From the `soundsource` directory:  
   `python engine/soundsource.py`

2. Change `user_risk_tolerance` in the call (0.0 = very conservative, 1.0 = aggressive).

3. Edit `sources/real_yield_sources.json` — lower a sustainability score and re-run. Observe the filter.

4. Add a new row to the ledger and confirm it appears in notes if confidence is low/medium.

5. Edge case: set all sustainability_score < 0.4 → allocation should be empty or minimal.

## Interpretation

- Weights sum to ~1.0.
- Emissions-dependent low-sustainability sources are excluded by principle.
- Scores favor real-yield durability over headline APY.

This prototype is ready for local testing and extension with live data.
