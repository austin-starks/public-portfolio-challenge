<div align="center">

# Public Portfolio Challenge

**One open runbook. Real money. AI agents that have to prove it out of sample before they deploy.**

<br />

[![Live portfolio](https://img.shields.io/badge/Live-$25K_portfolio-22c55e?style=for-the-badge)](https://nexustrade.io/shared-portfolio/69a7dc7cf99e43688fcec567)
[![MCP](https://img.shields.io/badge/Connect-via_MCP-4bc0c0?style=for-the-badge)](https://nexustrade.io/developers)
[![Runbook](https://img.shields.io/badge/Paste-the_runbook-c9a84c?style=for-the-badge)](episode-10/BAKEOFF_RUNBOOK.md)
[![No clone](https://img.shields.io/badge/No_code-checkout-64748b?style=for-the-badge)](#get-started)

<br />

[![Public Portfolio Challenge — live performance](https://nexustrade-prod.nyc3.cdn.digitaloceanspaces.com/shared-portfolios/og/69a7dc7cf99e43688fcec567/latest-v4.png?v=2)](https://nexustrade.io/shared-portfolio/69a7dc7cf99e43688fcec567)

*Live portfolio card — generated from current positions. [Open the full dashboard →](https://nexustrade.io/shared-portfolio/69a7dc7cf99e43688fcec567)*

<br />

**Quick start:** [Connect MCP](#step-3--connect-your-ai-tool) → edit [`profile.json`](profile.json) → `python3 start.py` → **paste the output into a fresh agent chat**

</div>

---

## Contents

- [What is this?](#what-is-this)
- [What this repo gives you](#what-this-repo-gives-you)
- [How the runbook works](#how-the-runbook-works)
- [What's inside](#whats-inside)
- [Get started](#get-started)
- [More links](#more-links)

---

## What is this?

In February 2026 I deposited **$25,000** into a live [Public](https://public.com) brokerage account on NexusTrade and made the entire book public — every position, every fill, every model test, every bug, every failure.

Not paper. Not a backtest screenshot. **Real money, documented in real time.**

The live story is a blog series:

| | |
| --- | --- |
| **[Full series →](https://nexustrade.io/blog/series/public-portfolio-challenge)** | Ten episodes and counting: model bakeoffs, deploy day, production bugs, week-one gains, panic sells, engine rewrites, and the open runbook. |
| **[Episode 1 →](https://nexustrade.io/blog/im-giving-an-ai-access-to-my-public-trading-account-heres-how-you-can-watch-it-destroy-25000-20260228)** | Where it started — why $25k, why Public, why total transparency. |

**This repo is the open playbook.** The blog is my run. The runbook is yours.

---

## What this repo gives you

<table>
<tr>
<td width="33%" valign="top">

### No install

Connect the NexusTrade MCP server to Cursor, Claude, or any OAuth-capable client. No repo checkout. No API keys to rotate (OAuth is the default path).

</td>
<td width="33%" valign="top">

### One prompt

[`episode-10/BAKEOFF_RUNBOOK.md`](episode-10/BAKEOFF_RUNBOOK.md) is a self-contained agent brief — paste it into a fresh session and let the agent execute. It prescribes *what* must be true, never *how* to achieve it. New here? Take the [fast path](#get-started) instead — edit `profile.json` and paste one prompt.

</td>
<td width="33%" valign="top">

### Real rigor

Walk-forward validation, a held-out lockbox, deploy gates, and capital-posture rules. A high in-sample backtest number is never the headline.

</td>
</tr>
</table>

---

## How the runbook works

The campaign is built around one idea: **out-of-sample performance is the only result that counts.**

```mermaid
flowchart LR
  A["🔍 Search<br/><small>backtests & optimization</small>"] --> B["✓ Certify<br/><small>walk-forward folds</small>"]
  B --> C["🔒 Lockbox<br/><small>single-touch confirm</small>"]
  C --> D["🚀 Deploy<br/><small>live portfolio</small>"]
```

| Layer | Job |
| --- | --- |
| **Search** | Invent and tune candidate strategies fast — variants, sweeps, backtests. |
| **Certify** | Walk-forward: each fold optimizes in-sample, scores on held-out OOS the optimizer never saw. |
| **Lockbox** | A final untouched window. One touch. No peeking. |
| **Deploy** | Clone to a live portfolio, parity-check, attach monitoring. |

Fixed by the runbook: a 20-name watchlist, $25,000 capital, the fold calendar, the gates, the lockbox rules, and the deploy procedure. **Yours to design:** signals, structures, deltas, exits, sizing — anything that clears the gates is valid.

<details>
<summary><strong>The watchlist (20 names, frozen)</strong></summary>

<br />

`ANET` · `DUOL` · `HOOD` · `LLY` · `GS` · `META` · `TSM` · `AVGO` · `XOM` · `COP` · `OSCR` · `AMAT` · `ADI` · `DDOG` · `OKTA` · `NET` · `APP` · `GLD` · `MU` · `SNDK`

</details>

---

## What's inside

Each episode is a self-contained folder: the **runbook** to paste, plus the **campaign logs** from each operator/agent run.

```
episode-10/
├── BAKEOFF_RUNBOOK.md             ← paste this into a fresh MCP session
├── RUNBOOK_OG.md                  ← the original (Episode 1) runbook, kept for reference
├── snapshots/                     ← baseline + incumbent seed portfolios the runbook loads
├── FABLE_CAMPAIGN.MD              ← operator run log (Fable 5)
├── CLAUDE_CODE_CAMPAIGN_LOG_*.md  ← agent run log (Claude)
├── CODEX_CAMPAIGN_LOG_*.md        ← agent run log (Codex)
└── CURSOR_CAMPAIGN_LOG_*.md       ← agent run log (Cursor)
```

| File | What it is |
| --- | --- |
| [`profile.json`](profile.json) + [`start.py`](start.py) | **Start here (fast path).** Put your watchlist + risk tolerance in `profile.json`, run `python3 start.py`, paste one prompt — the agent builds *you* a personalized strategy. No runbook needed. |
| [`episode-10/BAKEOFF_RUNBOOK.md`](episode-10/BAKEOFF_RUNBOOK.md) | The agent brief you run — walk-forward validation, lockbox, deploy gates. Paste and execute top to bottom. |
| [`episode-10/RUNBOOK_OG.md`](episode-10/RUNBOOK_OG.md) | The original Episode-1 runbook, kept for reference (the brief has since expanded). |
| [`episode-10/snapshots/`](episode-10/snapshots) | Baseline A/B and incumbent seed portfolios the runbook loads via `create_portfolio`. |
| Campaign logs | Per-run logs from each operator/agent: [`FABLE_CAMPAIGN.MD`](episode-10/FABLE_CAMPAIGN.MD), [`CLAUDE_CODE_…`](episode-10/CLAUDE_CODE_CAMPAIGN_LOG_20260613T165226Z.md), [`CODEX_…`](episode-10/CODEX_CAMPAIGN_LOG_20260613T165248Z.md), [`CURSOR_…`](episode-10/CURSOR_CAMPAIGN_LOG_20260613T165224Z.md). |

Future episodes get their own folders (`episode-11/`, …) when the runbook or campaign parameters change materially.

---

## Get started

### Step 1 — Developers page

Open **[nexustrade.io/developers](https://nexustrade.io/developers)**.

[![NexusTrade Developers — MCP URL and Connect an AI tool](https://nexustrade-prod.nyc3.cdn.digitaloceanspaces.com/Blog/PublicPortfolioChallenge/setup-developers-mcp-jun12.png)](https://nexustrade.io/developers)

### Step 2 — Create a free account

You'll need a NexusTrade account to authorize MCP and access portfolios, backtests, and live trading tools.

[![Join NexusTrade](https://nexustrade-prod.nyc3.cdn.digitaloceanspaces.com/Blog/PublicPortfolioChallenge/setup-signup-jun12.png)](https://nexustrade.io/register)

### Step 3 — Connect your AI tool

**Recommended: OAuth.** No keys to copy, rotate, or leak. Sign in once in the browser when your client first calls a NexusTrade tool.

```
https://nexustrade.io/api/mcp
```

#### Cursor *(recommended)*

1. On the [Developers page](https://nexustrade.io/developers), expand **API Keys**.
2. Under **Connect an AI tool to NexusTrade**, click **Add to Cursor**.
3. OAuth runs automatically on first tool use.

[![Authorize Cursor → NexusTrade MCP](https://nexustrade-prod.nyc3.cdn.digitaloceanspaces.com/Blog/PublicPortfolioChallenge/setup-oauth-authorize-cursor-jun12.png)](https://nexustrade.io/developers)

[![Connected to Cursor](https://nexustrade-prod.nyc3.cdn.digitaloceanspaces.com/Blog/PublicPortfolioChallenge/setup-oauth-connected-cursor-jun12.png)](https://nexustrade.io/developers)

<details>
<summary><strong>Manual Cursor config</strong></summary>

```json
{
  "mcpServers": {
    "nexustrade": {
      "url": "https://nexustrade.io/api/mcp"
    }
  }
}
```

</details>

<details>
<summary><strong>Claude Desktop / Claude Code</strong></summary>

Click **Copy install command** on the Developers page, or:

```bash
claude mcp add nexustrade --transport http https://nexustrade.io/api/mcp
```

</details>

<details>
<summary><strong>VS Code, ChatGPT, Windsurf, Zed, and other MCP clients</strong></summary>

Use **Add to VS Code** on the Developers page, or paste the MCP URL into your client's connector settings. OAuth 2.1 discovery works the same everywhere.

</details>

<details>
<summary><strong>Advanced: API keys</strong></summary>

For scripts without OAuth support: expand **Advanced: API Keys** on the Developers page and pass the key in the `Authorization` header. See the [API Reference](https://nexustrade.io/docs/api-reference/overview).

</details>

### Step 4 — Run it

**Fast path — a personalized strategy in one paste.** Edit [`profile.json`](profile.json) with your watchlist, risk tolerance, and asset classes (it ships with mine), then:

```bash
python3 start.py        # prints a ready-to-paste prompt
```

Paste the output into a **fresh** MCP-connected chat. No Python? Just paste `profile.json` itself with one line: *"Build me a personalized strategy from this profile, backtest it out-of-sample, and ask before deploying."* The agent designs a strategy on your names, backtests it, compares it to buy-and-hold, and **asks before risking a dollar**.

<details>
<summary><strong><code>profile.json</code> fields</strong></summary>

- `risk_tolerance` — `conservative` · `moderate` · `aggressive`
- `asset_classes` — any of `stocks`, `crypto`, `options`
- `watchlist` — the only tickers the agent may trade
- `capital` — starting USD

</details>

**Full rigor — the runbook.** Want walk-forward validation, a held-out lockbox, and deploy gates? Open [`episode-10/BAKEOFF_RUNBOOK.md`](episode-10/BAKEOFF_RUNBOOK.md), paste the **entire file** into a fresh session, and tell the agent: **execute top to bottom, do not ask clarifying questions.** Log your run alongside the per-agent campaign logs in `episode-10/`.

---

## More links

| | |
| --- | --- |
| [Live portfolio](https://nexustrade.io/shared-portfolio/69a7dc7cf99e43688fcec567) | Positions and P&L in real time |
| [Blog series](https://nexustrade.io/blog/series/public-portfolio-challenge) | The full documented journey |
| [Episode 1](https://nexustrade.io/blog/im-giving-an-ai-access-to-my-public-trading-account-heres-how-you-can-watch-it-destroy-25000-20260228) | How the challenge began |
| [Developers](https://nexustrade.io/developers) | MCP setup |
| [MCP tools reference](https://nexustrade.io/docs/api-reference/mcp-tools-utility) | Every tool the runbook can call |
| [API overview](https://nexustrade.io/docs/api-reference/overview) | REST + auth |

---

<div align="center">

<br />

**Fork it. Paste the runbook. Run the same discipline on your own idea.**

If it survives walk-forward and the lockbox, deploy it. If it doesn't, you found that out before risking a dollar.

<br />

[![NexusTrade](https://img.shields.io/badge/Built_on-NexusTrade-4bc0c0?style=flat-square)](https://nexustrade.io)
[![Follow live](https://img.shields.io/badge/Follow-live_P&L-22c55e?style=flat-square)](https://nexustrade.io/shared-portfolio/69a7dc7cf99e43688fcec567)

</div>
