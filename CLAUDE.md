# CLAUDE.md

MCP server wrapping the hapax cockpit API. Bridges 34 tools from the council/officium cockpit HTTP APIs to Claude Code via the Model Context Protocol.

Single-operator system — no auth on cockpit API.

## Build & Run

```bash
uv sync
uv run cockpit-mcp          # stdio transport
```

Configure in Claude Code `~/.claude/settings.json` under `mcpServers`.

## Project Structure

```
src/cockpit_mcp/
  server.py      MCP server, 34 tool definitions
  client.py      HTTP client for cockpit API (get/post/put/delete/post_sse)
  __init__.py    Package init
pyproject.toml   Project metadata, entry point
```

## Configuration

| Env Var | Default | Purpose |
|---------|---------|----------|
| `COCKPIT_BASE_URL` | `http://localhost:8051/api` | Cockpit API base URL |

HTTP timeout: 15 seconds.

## Tools

**Read-only (21):** health, health_history, briefing, scout, scout_decisions, drift, cost, goals, nudges, agents, gpu, infrastructure, cycle_mode, profile, profile_dimension, profile_pending, accommodations, copilot, readiness, workspace, manual

**Write (9):** nudge_act, nudge_dismiss, cycle_mode_set, profile_correct, profile_delete, profile_flush, scout_decide, accommodation_confirm, accommodation_disable

**Streaming (2):** query, query_refine — use SSE (collect text_delta/output events)

**Compound (2):** `status` = health + gpu + infrastructure + cycle_mode. `daily_summary` = briefing + nudges + goals + drift.

## Dependencies

- mcp >= 1.26
- httpx >= 0.28
- Python 3.12+
