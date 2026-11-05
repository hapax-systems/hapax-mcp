# CLAUDE.md

Experimental Model Context Protocol (`stdio`) research tooling from **Hapax Research Lab** ([hapaxresearch.com](https://hapaxresearch.com)). This package registers 38 MCP tools (including two deprecated aliases) bridging compatible MCP clients to an existing Logos HTTP API deployment. Endpoint availability depends on the configured backend; tool registration is not a backend compatibility check. Read [AGENTS.md](AGENTS.md) for repository rules.

Authority remains with the operator and the underlying Logos API. The bridge includes write tools and does not add an independent authorization policy or read-only mode. Optional bearer-token forwarding does not establish a backend's authentication requirements. Do not infer permission to act from a tool's availability.

## Deployment Context

This repository consumes a separately running Logos HTTP API and exposes bounded tools over MCP `stdio`:

- **Primary Logos API target** — default `http://localhost:8051/api`.
- **Secondary Logos API target** — selected via `LOGOS_BASE_URL` (for example `http://localhost:8050/api`).

Do not claim capability parity across separate backend deployments or client surfaces. Use a distinctly named MCP server entry to target a second backend URL.

## Build & Run

Requires Python 3.12+, `uv`, a checkout of this repository, and a reachable Logos API service. From the repository root:

```bash
uv sync --locked
uv run hapax-mcp          # stdio transport
```

The process waits for JSON-RPC input over `stdio`; it does not start a Logos API server. Use the [README setup instructions](README.md#register-in-claude-code) to register it with an MCP client, then call `health` to verify backend connectivity.

## Project Structure

```
src/hapax_mcp/
  server.py      MCP server, 38 tool definitions
  client.py      HTTP client for Logos API (get/post/put/delete/post_sse)
  models/        Pydantic response models (health, infrastructure, profile, working_mode)
  __init__.py    Package init
tests/           pytest suite (test_tools.py, test_response_models.py)
pyproject.toml   Project metadata and entry point
```

## Configuration

| Env Var | Default | Purpose |
|---------|---------|---------|
| `LOGOS_BASE_URL` | `http://localhost:8051/api` | Logos API base URL |
| `LOGOS_API_KEY` | unset | Optional bearer token forwarded to the backend |

`COCKPIT_BASE_URL` and `COCKPIT_API_KEY` are accepted as fallbacks when the corresponding `LOGOS_*` variable is unset. Supply secrets through the deployment's secret manager; never commit token values.

Standard-request HTTPX timeout: 15 seconds.

## Tools (38 registered)

**Inspection via GET (22):** `health`, `health_history`, `briefing`, `scout`, `scout_decisions`, `drift`, `cost`, `goals`, `nudges`, `agents`, `gpu`, `infrastructure`, `working_mode` (canonical), `cycle_mode` (deprecated alias), `profile`, `profile_dimension`, `profile_pending`, `accommodations`, `copilot`, `readiness`, `workspace`, `manual`

**Chronicle (2):** `chronicle` (query with `since`/`until`/`source`/`event_type`/`trace_id`/`limit` filters), `chronicle_narrate` (GET requesting a backend LLM synthesis; can incur model work)

**Write (10):** `nudge_act`, `nudge_dismiss`, `working_mode_set` (canonical), `cycle_mode_set` (deprecated alias), `profile_correct`, `profile_delete`, `profile_flush`, `scout_decide`, `accommodation_confirm`, `accommodation_disable`

**Query (2):** `query`, `query_refine` — POST to backend SSE endpoints and collect text into a single MCP tool response. Backend model configuration and usage costs apply.

**Compound (2):** `status` (`health` + `gpu` + `infrastructure` + `working_mode`), `daily_summary` (`briefing` + `nudges` + `goals` + `drift`).

Mode values: the MCP schemas for `working_mode_set` and `cycle_mode_set` accept `research`, `rnd`, or `fortress`; a backend deployment may accept a narrower subset. Both route to `/working-mode`. Legacy `dev` / `prod` values are outside the MCP schema.

## Gotchas

- **Response truncation:** JSON-formatted results are truncated after 50,000 characters and may cease to be valid JSON. SSE collection stops after reaching 1,000 chunks or 1 MiB; the final chunk can cross the byte threshold.
- **SSE timeouts:** HTTPX timeout is 120s and per-line wait is 30s; neither is a total stream-duration deadline.
- **Path validation:** Tools accepting path segments validate against `[a-zA-Z0-9_-]+` and raise `ValueError` on invalid input.
- **Error handling:** Handled HTTP status, connection, and timeout errors use `_fmt_error()`. Validation and other unhandled failures may surface as MCP tool errors; compound tools retain per-endpoint errors.
- **External content notice:** The server emits a static warning that tool output may include untrusted external text; this warning is client guidance, not sanitization or authorization enforcement.

## Verify the Source

From the repository root after `uv sync --locked`, inspect registered tools and implementation defaults without calling a backend:

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
```

Run the repository quality checks:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest tests -q
```

Hosted CI definitions live in [.github/workflows/ci.yml](.github/workflows/ci.yml).
