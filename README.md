<!-- hapax-sdlc:preamble:begin -->

# hapax-mcp

This repository is a constituent of the Hapax operating environment. It is not a product, not a service, and not seeking contributors. It is research infrastructure published as artifact.

Authorship is indeterminate by design: this codebase is co-produced by Hapax (the system itself), Claude Code, and the operator (Oudepode). Per the Hapax Manifesto, unsettled contribution is a feature of the work, not a concealment.

## What this is, not what it does

Constituent of the Hapax operating environment. Model Context Protocol server bridging the logos APIs to Claude Code. Single-operator MCP surface; not a general-purpose MCP library.

## Constitutional position

- Single-operator system; no auth, no roles, no contributor onboarding (axiom: `single_user`)
- No issues, no discussions, no PRs accepted; refusal is the artifact (see `CONTRIBUTING.md`)
- License: MIT (MCP ecosystem alignment)
- Citation: see `CITATION.cff`; archival DOI: see `.zenodo.json`

## Linked artifacts

- Manifesto: https://hapax.weblog.lol/hapax-manifesto-v0
- Refusal Brief: https://hapax.weblog.lol/refusal-brief
- Cohort Disparity Disclosure: https://hapax.weblog.lol/cohort-disparity-disclosure
- Constitution: https://github.com/hapax-systems/hapax-constitution

## Inter-repo position

MCP bridge. Consumes the council and officium logos APIs over HTTP and presents 38 tools to Claude Code. The MCP ecosystem norm is MIT; this repo carries MIT explicitly per operator divergence (every other runtime repo is PolyForm Strict).

<!-- hapax-sdlc:preamble:end -->

## Description

Model Context Protocol server (FastMCP, stdio transport) that exposes the Hapax logos HTTP APIs as MCP tools. The default endpoint is the council logos API at `http://localhost:8051/api`. Pointing `LOGOS_BASE_URL` at `http://localhost:8050/api` exposes the officium logos API instead.

The same logos data is reachable through three independent surfaces: the hapax-logos Tauri app, the VS Code extensions in [hapax-council](https://github.com/hapax-systems/hapax-council) and [hapax-officium](https://github.com/hapax-systems/hapax-officium), and this MCP server. Surface choice is operator preference; capability is identical across surfaces.

## Tool surface (38 tools)

| Group | Count | Tools |
|-------|-------|-------|
| Read-only | 22 | health, health_history, briefing, scout, scout_decisions, drift, cost, goals, nudges, agents, gpu, infrastructure, profile, profile_dimension, profile_pending, accommodations, copilot, readiness, workspace, manual, working_mode, cycle_mode |
| Chronicle | 2 | chronicle, chronicle_narrate |
| Write | 10 | nudge_act, nudge_dismiss, working_mode_set, cycle_mode_set, profile_correct, profile_delete, profile_flush, scout_decide, accommodation_confirm, accommodation_disable |
| Streaming (SSE) | 2 | query, query_refine |
| Compound | 2 | status (health + gpu + infrastructure + working_mode), daily_summary (briefing + nudges + goals + drift) |

`working_mode` and `working_mode_set` are canonical. `cycle_mode` and `cycle_mode_set` are deprecated aliases retained during the workspace-wide migration; both route through to `/working-mode` server-side. Accepted mode values: `research`, `rnd`, `fortress` (officium omits `fortress`). The legacy `dev` / `prod` values return 422 server-side.

`chronicle` accepts filters `since`, `until`, `source`, `event_type`, `trace_id`, `limit`. `chronicle_narrate` produces an LLM synthesis of a chronicle window.

## Install

```bash
uv sync
uv run hapax-mcp
```

Python 3.12+. Dependencies: `mcp>=1.26`, `httpx>=0.28.1`, `pydantic>=2.0`. Entry point: `hapax_mcp.server:main` (defined in `pyproject.toml`).

## Register in Claude Code

Add to `~/.claude/settings.json` under `mcpServers`:

```json
{
  "mcpServers": {
    "hapax": {
      "command": "uv",
      "args": ["--directory", "/path/to/hapax-mcp", "run", "hapax-mcp"],
      "env": {
        "LOGOS_BASE_URL": "http://localhost:8051/api"
      }
    }
  }
}
```

To bridge the officium API as well, register a second instance with `LOGOS_BASE_URL=http://localhost:8050/api`.

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `LOGOS_BASE_URL` | `http://localhost:8051/api` | Logos API base URL |
| `LOGOS_API_KEY` | unset | Optional bearer token; sent as `Authorization: Bearer …` if set |
| `COCKPIT_BASE_URL` | unset | Backward-compatible fallback for `LOGOS_BASE_URL` |
| `COCKPIT_API_KEY` | unset | Backward-compatible fallback for `LOGOS_API_KEY` |

HTTP timeout: 15s for standard requests; 120s overall for SSE streams; 30s per-event timeout aborts a stalled stream. Response bodies are truncated at 50,000 characters; SSE streams are truncated at 1,000 chunks or 1 MiB total. Path segments accepted by tools are validated against `[a-zA-Z0-9_-]+`.

Errors are caught and formatted into user-facing strings via `_fmt_error()`; no exceptions are raised across the MCP boundary.

## Project layout

```
src/hapax_mcp/
  server.py      MCP server, 38 tool definitions
  client.py      HTTP client, env var contract, timeouts
  models/        Pydantic response models (health, infrastructure, profile, working_mode)
tests/           pytest suite (test_tools.py, test_response_models.py)
pyproject.toml   Package metadata, entry point, deps
```

The server emits a static instruction warning that tool output may include content from external sources and should not be treated as instructions. This is consistent with the `interpersonal_transparency` axiom in the upstream constitution.

## CI

| Workflow | Trigger | Effect |
|----------|---------|--------|
| `ci.yml` | push main, PR | ruff check + format, pyright, gitleaks, bandit |
| `auto-fix.yml` | CI failure on PR | Claude Code attempts a fix; max 3 attempts per branch |
| `claude-review.yml` | PR open / sync | Claude Code review on the PR |
| `dependabot-auto-merge.yml` | Dependabot PR | Auto-merge for patch / minor bumps |

## Ecosystem

| Repository | Role |
|-----------|------|
| [hapax-council](https://github.com/hapax-systems/hapax-council) | Primary research artifact — voice daemon, grounding system, experiment infrastructure |
| [hapax-constitution](https://github.com/hapax-systems/hapax-constitution) | Governance specification — axioms, implications, canons, precedents |
| [hapax-officium](https://github.com/hapax-systems/hapax-officium) | Supporting software — management decision support |
| [hapax-watch](https://github.com/hapax-systems/hapax-watch) | Wear OS biometric companion |
| [hapax-phone](https://github.com/hapax-systems/hapax-phone) | Android health + context companion |
| **hapax-mcp** (this repo) | MCP server bridging the logos APIs to Claude Code |

## License

MIT — see [LICENSE](LICENSE).
