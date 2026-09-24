# CLAUDE.md

MCP stdio bridge for a Hapax operator's existing Logos API deployment. The
source registers 38 tools, including two deprecated aliases. Endpoint
availability depends on the configured backend; tool registration is not an
API compatibility check. Read [AGENTS.md](AGENTS.md) for repository rules.

Authority remains with the operator and the underlying API. The bridge has
write tools and does not add its own authorization policy or read-only mode.
Optional bearer-token forwarding does not establish a backend's authentication
requirements. Do not infer permission to act from a tool's availability.

## Sister surfaces

This repository consumes the Logos API over HTTP and exposes tools over MCP
stdio. Other clients' coverage and availability must be checked separately:

- **Council backend** — [hapax-council](https://github.com/hapax-systems/hapax-council), default `http://localhost:8051/api`.
- **Officium backend** — [hapax-officium](https://github.com/hapax-systems/hapax-officium), selected through `LOGOS_BASE_URL`, commonly `http://localhost:8050/api`.
- **Former Logos/Tauri shell** — [retired](https://github.com/hapax-systems/hapax-council/blob/main/docs/runbooks/tauri-logos-decommission.md).

Do not claim capability parity among these deployments or other clients.
Use a separately named MCP instance to target a second backend.

## Build & Run

Requires Python 3.12+, uv, this repository's source checkout, and a separately
running, reachable Logos API. From the repository root:

```bash
uv sync --locked
uv run hapax-mcp          # stdio transport
```

The process waits for MCP input; it does not start the Logos API. Use the
[README setup instructions](README.md#register-in-claude-code) to register it
with the client, then call `health` to check backend connectivity. A source
version or successful process launch is not a package-release or backend-health
receipt.

## Project Structure

```
src/hapax_mcp/
  server.py      MCP server, 38 tool definitions
  client.py      HTTP client for logos API (get/post/put/delete/post_sse)
  models/        Pydantic response models (health, infrastructure, profile, working_mode)
  __init__.py    Package init
pyproject.toml   Project metadata, entry point
```

## Configuration

| Env Var | Default | Purpose |
|---------|---------|----------|
| `LOGOS_BASE_URL` | `http://localhost:8051/api` | Logos API base URL |
| `LOGOS_API_KEY` | unset | Optional bearer token forwarded to the backend |

`COCKPIT_BASE_URL` and `COCKPIT_API_KEY` are fallbacks when the corresponding
`LOGOS_*` variable is absent. Resolve secrets through the deployment's secret
mechanism; never commit token values.

Standard-request HTTPX timeout: 15 seconds.

## Tools

**Inspection via GET (22):** health, health_history, briefing, scout, scout_decisions, drift, cost, goals, nudges, agents, gpu, infrastructure, working_mode (canonical), cycle_mode (deprecated alias), profile, profile_dimension, profile_pending, accommodations, copilot, readiness, workspace, manual

**Chronicle (2):** chronicle (query with since/until/source/event_type/trace_id/limit filters), chronicle_narrate (GET requesting a backend LLM synthesis; can incur model work)

**Write (10):** nudge_act, nudge_dismiss, working_mode_set (canonical), cycle_mode_set (deprecated alias), profile_correct, profile_delete, profile_flush, scout_decide, accommodation_confirm, accommodation_disable

**Query (2):** query, query_refine — POST to backend SSE endpoints, collect text
into one MCP tool response. Backend model configuration and usage costs apply.

**Compound (2):** `status` = health + gpu + infrastructure + working_mode. `daily_summary` = briefing + nudges + goals + drift.

Mode values: the MCP schemas for `working_mode_set` and `cycle_mode_set` accept
`research`, `rnd`, or `fortress`; a backend may accept fewer modes. Both route
to `/working-mode`. Legacy `dev` / `prod` values are outside the MCP schema.

## Gotchas

- **Response truncation:** JSON-formatted results are truncated after 50,000 characters and may cease to be valid JSON. SSE collection stops after reaching 1,000 chunks or 1 MiB; the last chunk can exceed the byte threshold.
- **SSE timeouts:** HTTPX timeout: 120s. Wait for each next line: 30s. Neither is a total stream-duration deadline.
- **Path validation:** Tools accepting user path segments validate against `[a-zA-Z0-9_-]+` — invalid inputs raise ValueError.
- **Error handling:** Handled HTTP status, connection, and timeout errors use `_fmt_error()`. Validation and other unhandled failures may surface as MCP tool errors; compound tools retain per-endpoint errors.
- **API key optional:** Bearer auth only sent if `LOGOS_API_KEY` (or `COCKPIT_API_KEY` fallback) env var is set.
- **External content:** The server warns that tool output is untrusted. That instruction does not enforce sanitization or authorization.

## Verify the source

From the repository root after `uv sync --locked`, inspect the registered tools
and implementation defaults without making backend requests:

```bash
uv run python - <<'PY'
import asyncio
import inspect

from hapax_mcp import client, server

tools = asyncio.run(server.mcp.list_tools())
print(f"{len(tools)} tools:", ", ".join(tool.name for tool in tools))
print("HTTP/SSE/next-line timeouts:", client._TIMEOUT, client._SSE_TIMEOUT, client._SSE_EVENT_TIMEOUT)
print("JSON defaults:", inspect.signature(server._sanitize_response))
print("SSE defaults:", inspect.signature(client.post_sse))
print("Path pattern:", server._PATH_SEGMENT_RE.pattern)
PY

uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest tests -q
```

These checks inspect this checkout; they do not establish backend availability
or cross-client compatibility. The hosted job definitions are in
[CI](.github/workflows/ci.yml).

## Dependencies

- mcp >= 1.26
- httpx >= 0.28.1
- pydantic >= 2.0
- Python 3.12+

> Subject to the workspace CLAUDE.md rotation policy: `hapax-council/docs/superpowers/specs/2026-04-13-claude-md-excellence-design.md`.
