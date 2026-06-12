# Public Portfolio Challenge

Build and deploy a momentum-based options strategy for a fixed 20-name watchlist on a live **$25,000** NexusTrade portfolio — using AI agents and the NexusTrade MCP server.

**Follow along in real time:** [Public Portfolio Challenge on NexusTrade](https://nexustrade.io/shared-portfolio/69a7dc7cf99e43688fcec567)

![Public Portfolio Challenge live dashboard](https://nexustrade-prod.nyc3.cdn.digitaloceanspaces.com/Blog/PublicPortfolioChallenge/public-portfolio-dashboard-may15.png)

This repo contains the runbook and campaign log. **No code checkout is required to execute the challenge** — everything runs through MCP tools once you're connected.

---

## Setup

### 1. Go to the Developers page

Open **[https://nexustrade.io/developers](https://nexustrade.io/developers)** in your browser.

![NexusTrade Developers page with MCP URL and Connect an AI tool section](https://nexustrade-prod.nyc3.cdn.digitaloceanspaces.com/Blog/PublicPortfolioChallenge/setup-developers-mcp-jun12.png)

### 2. Create a free account

Sign up for a free NexusTrade account if you don't already have one. You'll need it to authorize the MCP connection and access portfolios, backtests, and live trading tools.

![Join NexusTrade signup page](https://nexustrade-prod.nyc3.cdn.digitaloceanspaces.com/Blog/PublicPortfolioChallenge/setup-signup-jun12.png)

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

![Authorize Cursor to connect to NexusTrade via MCP](https://nexustrade-prod.nyc3.cdn.digitaloceanspaces.com/Blog/PublicPortfolioChallenge/setup-oauth-authorize-cursor-jun12.png)

![Connected to Cursor — switch back to start using NexusTrade](https://nexustrade-prod.nyc3.cdn.digitaloceanspaces.com/Blog/PublicPortfolioChallenge/setup-oauth-connected-cursor-jun12.png)

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

- [Public Portfolio Challenge (live)](https://nexustrade.io/shared-portfolio/69a7dc7cf99e43688fcec567) — follow positions and performance in real time
- [NexusTrade Developers](https://nexustrade.io/developers) — MCP setup and API keys
- [MCP Tools Reference](https://nexustrade.io/docs/api-reference/mcp-tools-utility)
- [API Overview](https://nexustrade.io/docs/api-reference/overview)
