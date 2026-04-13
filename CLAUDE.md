# CLAUDE.md

MCP server wrapping the hapax logos API. Bridges 36 tools from the council/officium logos HTTP APIs to Claude Code via the Model Context Protocol.

Single-operator system — no auth on logos API.

## Build & Run

```bash
uv sync
uv run hapax-mcp          # stdio transport
```

Configure in Claude Code `~/.claude/settings.json` under `mcpServers`.

## Project Structure

```
src/hapax_mcp/
  server.py      MCP server, 36 tool definitions
  client.py      HTTP client for logos API (get/post/put/delete/post_sse)
  models/        Pydantic response models (health, infrastructure, profile, working_mode)
  __init__.py    Package init
pyproject.toml   Project metadata, entry point
```

## Configuration

| Env Var | Default | Purpose |
|---------|---------|----------|
| `LOGOS_BASE_URL` | `http://localhost:8051/api` | Logos API base URL |

`COCKPIT_BASE_URL` and `COCKPIT_API_KEY` are accepted as fallbacks for backward compatibility.

HTTP timeout: 15 seconds.

## Tools

**Read-only (21):** health, health_history, briefing, scout, scout_decisions, drift, cost, goals, nudges, agents, gpu, infrastructure, cycle_mode, profile, profile_dimension, profile_pending, accommodations, copilot, readiness, workspace, manual

**Chronicle (2):** chronicle (query with since/until/source/event_type/trace_id/limit filters), chronicle_narrate (LLM-synthesized chronicle summary)

**Write (9):** nudge_act, nudge_dismiss, cycle_mode_set, profile_correct, profile_delete, profile_flush, scout_decide, accommodation_confirm, accommodation_disable

**Streaming (2):** query, query_refine — use SSE (collect text_delta/output events)

**Compound (2):** `status` = health + gpu + infrastructure + cycle_mode. `daily_summary` = briefing + nudges + goals + drift.

## Gotchas

- **Response truncation:** Read-only tool responses truncated at 50,000 characters. SSE streams truncated at 1,000 chunks or 1 MiB total.
- **SSE timeouts:** Per-event timeout: 30s (stream goes silent → abort). Overall SSE timeout: 120s.
- **Path validation:** Tools accepting user path segments validate against `[a-zA-Z0-9_-]+` — invalid inputs raise ValueError.
- **Error handling:** All errors caught and formatted via `_fmt_error()` — returns user-facing strings, not exceptions.
- **API key optional:** Bearer auth only sent if `LOGOS_API_KEY` (or `COCKPIT_API_KEY` fallback) env var is set.

## Dependencies

- mcp >= 1.26
- httpx >= 0.28
- pydantic >= 2.0
- Python 3.12+

## Known cross-repo inconsistency

The `cycle_mode` tool name (and `cycle_mode_set`, `/cycle-mode` endpoint) reflects this repo's current `server.py`. The workspace has otherwise migrated to `working_mode` (research/rnd) — this repo is the last holdout. Renaming requires a coordinated change here + in council's logos-api routes + in any Claude Code settings.json that pins the tool name. Out of scope for CLAUDE.md hygiene.

> Subject to the workspace CLAUDE.md rotation policy: `hapax-council/docs/superpowers/specs/2026-04-13-claude-md-excellence-design.md`.
