# Public Portfolio Challenge

Build and deploy a momentum-based options strategy for a fixed 20-name watchlist on a live **$25,000** NexusTrade portfolio — using AI agents and the NexusTrade MCP server.

**Follow along in real time:** [Public Portfolio Challenge on NexusTrade](https://nexustrade.io/shared-portfolio/69a7dc7cf99e43688fcec567)

[![Public Portfolio Challenge live dashboard — click to follow live](https://nexustrade-prod.nyc3.cdn.digitaloceanspaces.com/Blog/PublicPortfolioChallenge/public-portfolio-dashboard-may15.png)](https://nexustrade.io/shared-portfolio/69a7dc7cf99e43688fcec567)

## What is the Public Portfolio Challenge?

In February 2026 I deposited **$25,000** into a live [Public](https://public.com) brokerage account connected to NexusTrade and made the entire thing public — every position, every fill, every AI model test, every bug, every failure. Not a paper account. Not a backtest screenshot. Real money, documented in real time.

The point is **Trade-Driven Development**: instead of building features in isolation and hoping they help traders, I use my own live book as the forcing function. Can an AI-native platform actually help someone design, validate, and run a systematic options strategy — and can I prove it in public instead of hiding behind private Robinhood gains?

The ongoing story is told as a blog series on NexusTrade:

- **[The $25,000 Public Portfolio Challenge](https://nexustrade.io/blog/series/public-portfolio-challenge)** — the full series (episodes 1–9 and counting): model bakeoffs, deploy day, production bugs, week-one gains, panic sells, and everything in between.
- **[Episode 1: I'm giving an AI access to my Public trading account](https://nexustrade.io/blog/im-giving-an-ai-access-to-my-public-trading-account-heres-how-you-can-watch-it-destroy-25000-20260228)** — where it started: why $25k, why Public, why total transparency, and how to follow the live portfolio on NexusTrade.

**This repo is different from the blog.** The series documents *my* live run. This repo publishes the **runbook** — the exact agent brief I use to run a rigorous walk-forward validation campaign (multi-fold out-of-sample testing, a held-out lockbox, deploy gates) and push a strategy live through the NexusTrade MCP server. Fork it, paste [`RUNBOOK.md`](RUNBOOK.md) into your own AI session, and run the same discipline on your own idea.

**No code checkout is required** — everything runs through MCP tools once you're connected.

---

## Setup

### 1. Go to the Developers page

Open **[https://nexustrade.io/developers](https://nexustrade.io/developers)** in your browser.

[![NexusTrade Developers page with MCP URL and Connect an AI tool section — click to open](https://nexustrade-prod.nyc3.cdn.digitaloceanspaces.com/Blog/PublicPortfolioChallenge/setup-developers-mcp-jun12.png)](https://nexustrade.io/developers)

### 2. Create a free account

Sign up for a free NexusTrade account if you don't already have one. You'll need it to authorize the MCP connection and access portfolios, backtests, and live trading tools.

[![Join NexusTrade signup page — click to create a free account](https://nexustrade-prod.nyc3.cdn.digitaloceanspaces.com/Blog/PublicPortfolioChallenge/setup-signup-jun12.png)](https://nexustrade.io/register)

### 3. Connect an AI tool to NexusTrade

The recommended path is **OAuth** — no API keys to copy, rotate, or leak. Paste the MCP URL into your client and sign in once in the browser when prompted.

**MCP URL:**

```
https://nexustrade.io/api/mcp
```

#### Cursor (recommended)

1. On the [Developers page](https://nexustrade.io/developers), expand **API Keys**.
2. Under **Connect an AI tool to NexusTrade**, click **Add to Cursor**.
3. Cursor opens and registers the server. OAuth runs automatically the first time you use a NexusTrade tool.

[![Authorize Cursor to connect to NexusTrade via MCP](https://nexustrade-prod.nyc3.cdn.digitaloceanspaces.com/Blog/PublicPortfolioChallenge/setup-oauth-authorize-cursor-jun12.png)](https://nexustrade.io/developers)

[![Connected to Cursor — switch back to start using NexusTrade](https://nexustrade-prod.nyc3.cdn.digitaloceanspaces.com/Blog/PublicPortfolioChallenge/setup-oauth-connected-cursor-jun12.png)](https://nexustrade.io/developers)

Or add it manually in Cursor Settings → MCP:

```json
{
  "mcpServers": {
    "nexustrade": {
      "url": "https://nexustrade.io/api/mcp"
    }
  }
}
```

#### Claude Desktop / Claude Code

On the Developers page, click **Copy install command** under **Claude Desktop / Code**, then run it in your terminal. Claude runs the OAuth flow on the first tool call.

Example (if configuring manually):

```bash
claude mcp add nexustrade --transport http https://nexustrade.io/api/mcp
```

#### VS Code

Click **Add to VS Code** on the Developers page. OAuth runs on first tool call.

#### Other MCP clients

Using ChatGPT, Claude.ai, Windsurf, Zed, or another MCP client? Copy the URL above into that tool's connector settings — OAuth runs the same way. Works with any MCP client that supports OAuth 2.1 discovery.

#### Advanced: API keys

For scripts or tools that don't support OAuth, expand **Advanced: API Keys** on the Developers page, create a key, and pass it in the `Authorization` header. See the [API Reference](https://nexustrade.io/docs/api-reference/overview) for REST usage.

### 4. Run the challenge

Open a fresh AI session with the NexusTrade MCP server connected. Open [`RUNBOOK.md`](RUNBOOK.md), paste the whole file into the chat, and tell the agent to execute it top to bottom.

Optional: track progress in [`CAMPAIGN_LOG.md`](CAMPAIGN_LOG.md).

---

## Repo contents

| File | Purpose |
| ---- | ------- |
| [`RUNBOOK.md`](RUNBOOK.md) | Full agent brief — paste into a fresh MCP session |
| [`CAMPAIGN_LOG.md`](CAMPAIGN_LOG.md) | Example campaign log from a live run |

---

## Links

- [Public Portfolio Challenge (live portfolio)](https://nexustrade.io/shared-portfolio/69a7dc7cf99e43688fcec567) — positions and P&L in real time
- [Blog series](https://nexustrade.io/blog/series/public-portfolio-challenge) — the full documented journey
- [Episode 1 — how the challenge began](https://nexustrade.io/blog/im-giving-an-ai-access-to-my-public-trading-account-heres-how-you-can-watch-it-destroy-25000-20260228)
- [NexusTrade Developers](https://nexustrade.io/developers) — MCP setup and API keys
- [MCP Tools Reference](https://nexustrade.io/docs/api-reference/mcp-tools-utility)
- [API Overview](https://nexustrade.io/docs/api-reference/overview)
