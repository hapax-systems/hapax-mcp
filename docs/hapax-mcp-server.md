# Design: Cockpit MCP Server for Claude Code

**Date:** 2026-03-13
**Status:** Draft
**Author:** hapax + Claude

## 1. Current State

Claude Code accesses cockpit data via `curl` through the Bash tool:

```bash
curl -s http://localhost:8051/api/health | jq .
curl -s http://localhost:8051/api/briefing | jq .
curl -s http://localhost:8051/api/nudges | jq .
```

### Problems

- **Permission friction:** Every `curl` call requires Bash tool approval (or a pre-approved pattern in `settings.json`). The current allowlist covers `curl -s http://localhost*` but this is a blunt instrument.
- **No discoverability:** Claude Code has no idea what endpoints exist. It must be told or guess. There is no tool list, no parameter schema, no description.
- **Clunky output:** Raw JSON piped through `jq` wastes tokens on formatting. MCP tools can return structured data with annotations.
- **No write safety:** POST/PUT endpoints (cycle-mode switch, nudge acknowledge, profile correct) get the same Bash approval as harmless GETs. MCP tools can declare `readOnlyHint` / `destructiveHint` annotations so Claude Code applies appropriate confirmation UI.
- **SSE streams don't work:** Query dispatch and agent run return SSE streams. Bash `curl` either blocks forever or requires `timeout` hacks. MCP tools can consume the stream server-side and return the final result.

## 2. MCP Protocol Overview

### Architecture

```
Claude Code (client)
    │ stdin/stdout (JSON-RPC 2.0)
    ▼
hapax-mcp-server (Python, stdio transport)
    │ HTTP (aiohttp/httpx)
    ▼
cockpit-api (FastAPI, localhost:8051)
```

### How It Works

1. **Registration:** Claude Code reads `.mcp.json` (project scope) or `~/.claude.json` (local/user scope) for server definitions. For stdio servers, it spawns the process and communicates over stdin/stdout.

2. **Initialize handshake:** Client sends `initialize` with protocol version and capabilities. Server responds with its capabilities (tools, resources, prompts). Client sends `initialized` notification.

3. **Tool discovery:** Client sends `tools/list`. Server returns tool definitions with name, description, and JSON Schema for `inputSchema`.

4. **Tool invocation:** When the LLM decides to use a tool, Claude Code sends `tools/call` with tool name and arguments. Server executes, returns `content` (text, image, or structured JSON) with `isError` flag.

5. **Lifecycle:** Claude Code manages the subprocess. If the server crashes, Claude Code can restart it. The `listChanged` capability lets the server notify the client when tools are added/removed.

### Key Properties

- **Transport:** stdio (stdin/stdout). No network ports, no auth needed. The MCP server is a child process of Claude Code.
- **Protocol:** JSON-RPC 2.0 over newline-delimited messages.
- **Tool annotations:** `readOnlyHint`, `destructiveHint`, `openWorldHint` guide Claude Code's confirmation behavior.
- **Token limits:** Claude Code warns at 10,000 tokens of MCP output, hard limit at 25,000 (configurable via `MAX_MCP_OUTPUT_TOKENS`).

## 3. Tool Design

### 3.1 Read-Only Tools (always safe, `readOnlyHint: true`)

| MCP Tool | Cockpit Endpoint | Description |
|---|---|---|
| `cockpit_health` | `GET /api/health` | Service health: overall status, healthy/total counts, failed checks |
| `cockpit_health_history` | `GET /api/health/history` | Health status over time (for trend analysis) |
| `cockpit_briefing` | `GET /api/briefing` | Daily briefing: priorities, action items, context |
| `cockpit_scout` | `GET /api/scout` | Technology scout: upgrade candidates, security advisories |
| `cockpit_scout_decisions` | `GET /api/scout/decisions` | Past scout adoption/deferral decisions |
| `cockpit_drift` | `GET /api/drift` | Configuration drift: items diverging from declared state |
| `cockpit_cost` | `GET /api/cost` | LLM token spend: by model, by agent, trends |
| `cockpit_goals` | `GET /api/goals` | Active goals and progress |
| `cockpit_nudges` | `GET /api/nudges` | Pending nudges (actionable suggestions from agents) |
| `cockpit_agents` | `GET /api/agents` | Agent registry: names, commands, status |
| `cockpit_gpu` | `GET /api/gpu` | GPU/VRAM state: usage %, loaded models |
| `cockpit_infrastructure` | `GET /api/infrastructure` | Docker containers + systemd timers |
| `cockpit_cycle_mode` | `GET /api/cycle-mode` | Current cycle mode (dev/prod) and switch time |
| `cockpit_profile` | `GET /api/profile` | Operator profile summary: dimensions, fact counts |
| `cockpit_profile_dimension` | `GET /api/profile/{dimension}` | Facts for a specific profile dimension |
| `cockpit_profile_pending` | `GET /api/profile/facts/pending` | Pending profile observations not yet flushed |
| `cockpit_accommodations` | `GET /api/accommodations` | Active accommodations (accessibility/preference adjustments) |
| `cockpit_copilot` | `GET /api/copilot` | Context-aware copilot observation message |
| `cockpit_readiness` | `GET /api/readiness` | System readiness level and gaps |
| `cockpit_workspace` | `GET /api/workspace` | Workspace state (screen, camera, hardware) |
| `cockpit_manual` | `GET /api/manual` | Operations manual content |
| `cockpit_query_agents` | `GET /api/query/agents` | Available query agent types for dispatch |

### 3.2 Write Tools (`readOnlyHint: false`, need confirmation)

| MCP Tool | Cockpit Endpoint | Description |
|---|---|---|
| `cockpit_nudge_act` | `POST /api/nudges/{source_id}/act` | Mark a nudge as executed |
| `cockpit_nudge_dismiss` | `POST /api/nudges/{source_id}/dismiss` | Dismiss a nudge |
| `cockpit_cycle_mode_set` | `PUT /api/cycle-mode` | Switch between dev/prod mode |
| `cockpit_profile_correct` | `POST /api/profile/correct` | Correct a profile fact |
| `cockpit_profile_delete` | `POST /api/profile/delete` | Delete a profile fact |
| `cockpit_profile_flush` | `POST /api/profile/facts/flush` | Flush pending facts to profile |
| `cockpit_scout_decide` | `POST /api/scout/{component}/decide` | Record adoption/deferral/dismissal of a scout item |
| `cockpit_accommodation_confirm` | `POST /api/accommodations/{id}/confirm` | Activate an accommodation |
| `cockpit_accommodation_disable` | `POST /api/accommodations/{id}/disable` | Deactivate an accommodation |

### 3.3 Streaming Endpoints (adapted for MCP)

These cockpit endpoints return SSE streams. The MCP server will consume the full stream internally and return the final result as a single text response.

| MCP Tool | Cockpit Endpoint | Adaptation |
|---|---|---|
| `cockpit_query` | `POST /api/query/run` | Consume SSE stream, return final markdown + metadata (agent used, tokens, elapsed) |
| `cockpit_query_refine` | `POST /api/query/refine` | Same pattern, with prior context |

### 3.4 Excluded Endpoints

These are excluded from MCP because they require persistent sessions, real-time streaming, or are UI-specific:

- **Chat sessions** (`/api/chat/*`) -- Stateful multi-turn conversations with SSE. Claude Code already IS the chat interface; wrapping chat-in-chat adds no value.
- **Agent run** (`/api/agents/{name}/run`) -- Long-running subprocess with SSE output. Better invoked via Bash (`uv run agent scout`) where Claude Code can see the live output. Could be added later with a timeout.
- **Demo files** (`/api/demos/*/files/*`) -- Binary file serving. Not useful as MCP tool output.
- **Demo deletion** (`DELETE /api/demos/{id}`) -- Destructive, rare, better done explicitly via curl.

### 3.5 Compound / High-Value Tools

Beyond 1:1 endpoint mapping, the MCP server can offer compound tools that combine multiple calls:

| MCP Tool | Logic | Value |
|---|---|---|
| `cockpit_status` | `health` + `gpu` + `infrastructure` + `cycle_mode` in one call | Single-tool system snapshot, saves 4 round-trips |
| `cockpit_daily_summary` | `briefing` + `nudges` + `goals` + `drift` | Morning briefing in one call |

## 4. Implementation Approach

### Recommendation: Option A -- Python stdio server using `mcp` SDK

```
hapax-mcp/
├── pyproject.toml        # depends on: mcp, httpx
├── src/
│   └── cockpit_mcp/
│       ├── __init__.py
│       ├── server.py     # MCP server definition + tool handlers
│       └── client.py     # httpx client for cockpit API
└── README.md
```

**Why Option A:**

- The `mcp` Python SDK (`pip install mcp`) provides a decorator-based API (`@server.tool()`) that maps cleanly to our endpoint list.
- stdio transport means zero network configuration, zero auth. Claude Code spawns the process.
- Separate from cockpit's own venv avoids coupling deployment. The MCP server is a thin HTTP client.
- Can use `httpx.AsyncClient` with connection pooling for fast sequential calls.

### Why Not Option B (HTTP proxy)

An HTTP MCP transport would require Claude Code to connect over the network. This adds auth concerns and provides no benefit for a single-machine setup. stdio is simpler and more secure.

### Why Not Option C (cockpit serves MCP natively)

Embedding MCP into the FastAPI cockpit server would require adding a stdio transport alongside the existing HTTP server. This couples two concerns (web SPA serving + MCP protocol) and makes the cockpit harder to test independently. The MCP server should be a thin client, not a host modification.

### Implementation Skeleton

```python
from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP(
    "cockpit",
    instructions="Hapax cockpit system dashboard. Use these tools to check "
    "system health, read briefings, manage nudges, and query agents.",
)

COCKPIT_BASE = "http://localhost:8051/api"

async def _get(path: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{COCKPIT_BASE}{path}", timeout=10)
        resp.raise_for_status()
        return resp.json()

async def _post(path: str, json: dict | None = None) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{COCKPIT_BASE}{path}", json=json, timeout=30)
        resp.raise_for_status()
        return resp.json()


# ── Read-only tools ────────────────────────────────────────────────

@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False},
)
async def cockpit_health() -> dict:
    """Get system health status: overall status, healthy/total check counts,
    and list of any failed checks."""
    return await _get("/health")


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False},
)
async def cockpit_briefing() -> dict:
    """Get the daily briefing: priorities, action items, and system context.
    Updated every 5 minutes."""
    return await _get("/briefing")


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False},
)
async def cockpit_nudges() -> dict:
    """Get pending nudges -- actionable suggestions from hapax agents.
    Each nudge has a source_id for acting on or dismissing."""
    return await _get("/nudges")


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False},
)
async def cockpit_profile(dimension: str = "") -> dict:
    """Get operator profile. If dimension is provided, returns facts for
    that dimension. Otherwise returns a summary of all dimensions."""
    if dimension:
        return await _get(f"/profile/{dimension}")
    return await _get("/profile")


# ── Write tools ────────────────────────────────────────────────────

@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False},
)
async def cockpit_nudge_act(source_id: str) -> dict:
    """Mark a nudge as executed. Use cockpit_nudges first to see available
    nudges and their source_ids."""
    return await _post(f"/nudges/{source_id}/act")


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False},
)
async def cockpit_cycle_mode_set(mode: str) -> dict:
    """Switch cycle mode. Mode must be 'dev' or 'prod'.
    This affects agent behavior system-wide."""
    return await _post("/cycle-mode", json={"mode": mode})


# ── Query dispatch (SSE → collected result) ────────────────────────

@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": True},
)
async def cockpit_query(query: str) -> dict:
    """Run a natural language query against the hapax agent system.
    The query is auto-classified to the right agent (health, cost, drift,
    profile, etc.) and the agent's response is returned as markdown."""
    # Consume SSE stream, return final result
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST", f"{COCKPIT_BASE}/query/run",
            json={"query": query}, timeout=60,
        ) as resp:
            result = {"markdown": "", "agent_used": "", "tokens_in": 0,
                       "tokens_out": 0, "elapsed_ms": 0}
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    import json
                    data = json.loads(line[6:])
                    if "content" in data:
                        result["markdown"] = data["content"]
                    elif "agent_used" in data:
                        result.update(data)
            return result


# ── Compound tools ─────────────────────────────────────────────────

@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": False},
)
async def cockpit_status() -> dict:
    """Get a combined system status snapshot: health, GPU/VRAM,
    infrastructure (containers + timers), and cycle mode."""
    import asyncio
    health, gpu, infra, mode = await asyncio.gather(
        _get("/health"), _get("/gpu"),
        _get("/infrastructure"), _get("/cycle-mode"),
    )
    return {"health": health, "gpu": gpu,
            "infrastructure": infra, "cycle_mode": mode}
```

### SSE Stream Consumption

For the query dispatch and refine endpoints, the MCP server acts as an SSE client. It reads all events from the stream and returns the accumulated result. The `httpx` streaming API handles this cleanly. A 60-second timeout prevents indefinite blocking.

If the SSE stream errors, the tool returns `isError: true` with the error message from the `error` event.

## 5. Configuration

### Project-Scope (`.mcp.json` in distro-work root)

```json
{
  "mcpServers": {
    "cockpit": {
      "command": "uv",
      "args": ["--directory", "/home/operator/projects/hapax-mcp", "run", "hapax-mcp"],
      "env": {
        "COCKPIT_BASE_URL": "http://localhost:8051/api"
      }
    }
  }
}
```

### User-Scope (available across all projects)

```bash
claude mcp add --transport stdio --scope user \
  --env COCKPIT_BASE_URL=http://localhost:8051/api \
  cockpit -- uv --directory /home/operator/projects/hapax-mcp run hapax-mcp
```

User scope is recommended since cockpit is a system-level service, not project-specific.

### Verification

```bash
# List configured servers
claude mcp list

# Check server status inside Claude Code
/mcp
```

## 6. Tool Schemas (Examples)

### cockpit_health

```json
{
  "name": "cockpit_health",
  "description": "Get system health status: overall status, healthy/total check counts, and list of any failed checks.",
  "inputSchema": {
    "type": "object",
    "properties": {},
    "required": []
  },
  "annotations": {
    "readOnlyHint": true,
    "openWorldHint": false
  }
}
```

Response shape:
```json
{
  "overall_status": "healthy",
  "healthy": 12,
  "total_checks": 14,
  "failed_checks": ["ollama", "langfuse"]
}
```

### cockpit_briefing

```json
{
  "name": "cockpit_briefing",
  "description": "Get the daily briefing: priorities, action items, and system context. Updated every 5 minutes.",
  "inputSchema": {
    "type": "object",
    "properties": {},
    "required": []
  },
  "annotations": {
    "readOnlyHint": true,
    "openWorldHint": false
  }
}
```

### cockpit_nudge_act

```json
{
  "name": "cockpit_nudge_act",
  "description": "Mark a nudge as executed. Use cockpit_nudges first to see available nudges and their source_ids.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "source_id": {
        "type": "string",
        "description": "The source_id of the nudge to mark as executed"
      }
    },
    "required": ["source_id"]
  },
  "annotations": {
    "readOnlyHint": false,
    "destructiveHint": false
  }
}
```

### cockpit_query

```json
{
  "name": "cockpit_query",
  "description": "Run a natural language query against the hapax agent system. The query is auto-classified to the right agent (health, cost, drift, profile, etc.) and the agent's response is returned as markdown.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Natural language question about system state, costs, configuration, profile, etc."
      }
    },
    "required": ["query"]
  },
  "annotations": {
    "readOnlyHint": true,
    "openWorldHint": true
  }
}
```

## 7. Relationship to Existing Skills and Workflow

### Replaced by MCP Tools

The following `settings.json` permission patterns become less necessary:

```json
"Bash(curl -s http://localhost*)"
```

With MCP tools, Claude Code calls `cockpit_health` directly instead of composing a curl command. The Bash permission can remain for edge cases but won't be the primary access path.

### Complementary

- **Bash tool** remains needed for: `systemctl`, `journalctl`, `nvidia-smi`, `docker`, `pacman` -- anything not behind the cockpit API.
- **Session hooks** (`session-context.sh`) currently inject cockpit state into the conversation. With MCP, Claude Code can pull state on-demand rather than getting a dump at session start. The session hook could be simplified to just set context, with details fetched via MCP tools as needed.
- **CLAUDE.md diagnostic commands** remain the reference for direct system access. MCP tools are the cockpit layer above.

### New Capabilities

MCP enables workflows that were impractical with curl:

- **"Check the system and fix anything broken"** -- Claude Code calls `cockpit_status`, sees a failed health check, then uses Bash to investigate and fix. No curl composition needed.
- **"What should I work on?"** -- Claude Code calls `cockpit_daily_summary` (briefing + nudges + goals) in one tool call.
- **"Ask the system about X"** -- `cockpit_query` dispatches to the right agent and returns a synthesized answer. This replaces a multi-step curl + jq workflow.

## 8. Risks and Mitigations

### Cockpit Down

**Risk:** If the cockpit API is not running, all MCP tools fail.

**Mitigation:** Each tool catches `httpx.ConnectError` and returns a clear error message: "Cockpit API not reachable at localhost:8051. Start it with: `cd ~/projects/hapax-council && uv run cockpit`". The `isError: true` flag ensures Claude Code treats this as a tool failure, not a valid empty response.

### Token Budget

**Risk:** Large responses (full briefing, all nudges, operations manual) could exceed the MCP output token limit.

**Mitigation:**
- Set `MAX_MCP_OUTPUT_TOKENS=50000` in the environment for sessions that need large outputs.
- The compound tools (`cockpit_status`, `cockpit_daily_summary`) aggregate data server-side, reducing redundant framing.
- For `cockpit_manual` (which returns full markdown), consider truncation or summary mode.

### No Authentication

**Risk:** The cockpit API has no auth. Anyone on localhost can call it.

**Mitigation:** Acceptable for a single-user workstation. The MCP server runs as a child process of Claude Code, which runs as the user. The cockpit only listens on localhost. No change needed.

### Rate Limiting

**Risk:** Claude Code could hammer the cockpit API with rapid tool calls.

**Mitigation:** The cockpit already caches data (30s fast, 5min slow). Repeated calls return cached data instantly. The MCP server could add a client-side cache for read-only tools (e.g., don't re-fetch health within 10 seconds) but this is an optimization, not a requirement.

### Query Dispatch Cost

**Risk:** `cockpit_query` invokes an LLM call through the cockpit (LiteLLM -> model). Claude Code using an LLM tool that itself calls an LLM is a cost multiplier.

**Mitigation:** Tool description makes this explicit: "This invokes an LLM agent on the cockpit side." Claude Code can decide whether to use the tool or answer directly from cached data. The query tool is most valuable for questions requiring cockpit-side data aggregation that Claude Code can't do directly.

## 9. Implementation Plan

1. **Scaffold project** -- `uv init hapax-mcp` with dependencies `mcp`, `httpx`
2. **Implement read-only tools** (health, briefing, scout, drift, cost, goals, nudges, profile, gpu, infrastructure, cycle-mode, accommodations, copilot, readiness) -- ~20 tools, all following the same `_get()` pattern
3. **Implement write tools** (nudge act/dismiss, cycle-mode set, profile correct/delete/flush, scout decide, accommodation confirm/disable) -- ~9 tools
4. **Implement SSE consumer tools** (query run, query refine) -- 2 tools with stream consumption
5. **Implement compound tools** (status, daily_summary) -- 2 tools
6. **Register in Claude Code** -- `claude mcp add --scope user`
7. **Test** -- Verify each tool category works, test error handling (cockpit down, bad input, timeout)
8. **Iterate** -- Adjust tool descriptions based on how well Claude Code discovers and uses them

Estimated effort: 2-3 hours for a working v1.
