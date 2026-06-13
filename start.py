#!/usr/bin/env python3
"""Build your trading profile and generate an agent prompt.

    python3 start.py

- First run (no profile.json): walks you through a few questions and writes profile.json.
- After that: just reads your profile.json.

Either way it writes your ready-to-paste agent prompt to prompt.txt.
No dependencies.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).parent
PROFILE = HERE / "profile.json"
EXAMPLE = HERE / "example_profile.json"
OUT = HERE / "prompt.txt"

RISK = {
    "conservative": "Favor defined-risk structures, broad diversification, and modest sizing. Protect capital; keep drawdowns small.",
    "moderate": "Balance growth and risk: reasonable diversification, moderate sizing, some convexity but cap the downside.",
    "aggressive": "Lean into convex, higher-upside expressions and concentration in the strongest names. Larger drawdowns are acceptable for more upside.",
}


def ask(label, default):
    shown = ", ".join(default) if isinstance(default, list) else str(default)
    try:
        ans = input(f"{label}\n  [{shown}]: ").strip()
    except EOFError:
        ans = ""  # non-interactive: accept the default
    return ans or shown


def wizard():
    ex = json.loads(EXAMPLE.read_text()) if EXAMPLE.exists() else {}
    print("No profile.json yet — let's build one. Press Enter to accept each [default].\n")
    name = ask("Name this book", ex.get("name", "My book"))
    capital = ask("Starting capital (USD)", ex.get("capital", 10000))
    risk = ask("Risk tolerance (conservative / moderate / aggressive)", ex.get("risk_tolerance", "moderate")).lower()
    classes = ask("Asset classes (comma-separated: stocks, crypto, options)", ex.get("asset_classes", ["stocks"]))
    watchlist = ask("Watchlist tickers (comma-separated)", ex.get("watchlist", []))
    notes = ask("Notes for the agent (optional)", ex.get("notes", ""))

    profile = {
        "name": name,
        "capital": int(float(str(capital).replace(",", "").replace("$", "") or 10000)),
        "risk_tolerance": risk if risk in RISK else "moderate",
        "asset_classes": [c.strip().lower() for c in str(classes).split(",") if c.strip()],
        "watchlist": [t.strip().upper() for t in str(watchlist).split(",") if t.strip()],
        "notes": str(notes),
    }
    PROFILE.write_text(json.dumps(profile, indent=2) + "\n")
    print(f"\n  Wrote {PROFILE.name}")
    return profile


def build_prompt(p):
    risk = str(p.get("risk_tolerance", "moderate")).lower()
    risk_line = RISK.get(risk, RISK["moderate"])
    classes = ", ".join(p.get("asset_classes", ["stocks"]))
    tickers = ", ".join(p.get("watchlist", []))
    notes = str(p.get("notes", "")).strip()
    return f"""You have the NexusTrade MCP server connected. Build and validate a personalized
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


def main():
    profile = json.loads(PROFILE.read_text()) if PROFILE.exists() else wizard()
    OUT.write_text(build_prompt(profile) + "\n")
    print(f"\n  Wrote your agent prompt -> {OUT.name}")
    print("  Open it, copy everything, and paste into a fresh NexusTrade MCP chat.\n")


if __name__ == "__main__":
    main()
