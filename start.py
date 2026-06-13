#!/usr/bin/env python3
"""Turn profile.json into a copy-paste prompt for your NexusTrade MCP agent.

    python3 start.py        # prints the prompt — copy it into a fresh agent chat

No dependencies. Edit profile.json first, then run this.
"""
import json
import pathlib

p = json.loads(pathlib.Path(__file__).with_name("profile.json").read_text())

RISK = {
    "conservative": "Favor defined-risk structures, broad diversification, and modest sizing. Protect capital; keep drawdowns small.",
    "moderate": "Balance growth and risk: reasonable diversification, moderate sizing, some convexity but cap the downside.",
    "aggressive": "Lean into convex, higher-upside expressions and concentration in the strongest names. Larger drawdowns are acceptable for more upside.",
}

risk = str(p.get("risk_tolerance", "moderate")).lower()
risk_line = RISK.get(risk, RISK["moderate"])
classes = ", ".join(p.get("asset_classes", ["stocks"]))
tickers = ", ".join(p.get("watchlist", []))
notes = str(p.get("notes", "")).strip()

prompt = f"""You have the NexusTrade MCP server connected. Build and validate a personalized
trading strategy for me, and ask before doing anything with real money.

My profile:
- Capital: ${p.get('capital', 10000):,}
- Risk tolerance: {risk} — {risk_line}
- Asset classes to use: {classes}
- Watchlist (only trade these): {tickers}""" + (f"\n- Notes: {notes}" if notes else "") + """

Please, using the NexusTrade MCP tools:
1. Design a strategy that fits my risk tolerance and asset classes, restricted to my watchlist.
2. Backtest it and show me the results. Out-of-sample / held-out performance is the number
   that matters — not a single in-sample backtest.
3. Compare it to simply buying and holding my watchlist.
4. Iterate once or twice to improve it, explaining each change.
5. STOP and ask me before deploying anything live. Never trade real money without my explicit OK.

Explain your reasoning as you go and keep me in the loop."""

print(prompt)
