<!-- hapax-sdlc:preamble:begin -->

# hapax-mcp

`hapax-mcp` is an integration bridge for the Hapax Systems portfolio. It is maintained for MCP integration and inspection, not as a general-purpose framework.

## Reader promise

MCP bridge exposing Hapax logos API state and actions to Claude Code and compatible MCP clients.

## Reader value

Gives MCP clients a bounded bridge to live Hapax state while keeping authority with the underlying APIs rather than the connector.

## Claim ceiling

Integration bridge only; not a general MCP framework and not an authority source beyond the underlying Hapax APIs.

## License and rights

Permissive integration bridge for MCP use; current copy must frame it as a Hapax logos bridge, not a general-purpose MCP library.

Rendered summary: MIT. See `LICENSE`, `NOTICE.md`, `CITATION.cff`, and `.zenodo.json` for the authority surfaces.

## Public boundary

- Issues are redirect-only; no discussions, no pull requests accepted; see `CONTRIBUTING.md` and `SUPPORT.md`
- Public copy must use `hapax-systems` organization links for first-party Hapax repositories.
- Publication, weblog, RSS, social, DOI/archive, and other public fanout paths must route through the governed publication bus or a documented guarded legacy surface.
- Governance reference: https://github.com/hapax-systems/hapax-constitution

## Portfolio position

MCP bridge. Consumes council and officium logos APIs over HTTP and presents bounded tools to Claude Code and compatible MCP clients. Authority remains with the underlying Hapax APIs.

<!-- hapax-sdlc:preamble:end -->

## Description

`hapax-mcp` lets a Hapax operator inspect system state and request API actions
from Claude Code or another MCP client that can launch a local stdio server.
It uses FastMCP to translate tool calls into HTTP requests to a **separately
running Logos API**. Installing this repository installs the bridge; it does
not install or start the Hapax runtime.

The default backend is the [hapax-council](https://github.com/hapax-systems/hapax-council)
Logos API at `http://localhost:8051/api`. Set `LOGOS_BASE_URL` to a reachable
[hapax-officium](https://github.com/hapax-systems/hapax-officium) Logos API
(such as `http://localhost:8050/api`) to target that deployment instead.
Available endpoints and accepted operations depend on the backend version
and configuration; changing the URL does not establish tool compatibility.

The former [Logos/Tauri desktop shell is retired](https://github.com/hapax-systems/hapax-council/blob/main/docs/runbooks/tauri-logos-decommission.md).
Other clients may expose different capabilities. This bridge supplies neither
an independent authorization policy nor a read-only mode: it registers the
write tools below alongside inspection tools. The operator must authorize
client actions; the configured API remains responsible for enforcing its own
access and action policy.

## Tool surface (38 registered tools)

This is the inventory in [server.py](src/hapax_mcp/server.py), including two
deprecated aliases. Registration does not verify that a backend implements
every endpoint.

| Group | Count | Tools | Reader value |
|-------|-------|-------|---|
| Inspection (GET) | 22 | health, health_history, briefing, scout, scout_decisions, drift, cost, goals, nudges, agents, gpu, infrastructure, profile, profile_dimension, profile_pending, accommodations, copilot, readiness, workspace, manual, working_mode, cycle_mode | Gives MCP clients visibility into state without needing to own the underlying APIs. |
| Chronicle | 2 | chronicle, chronicle_narrate | Lets a client inspect and summarize event history with the source window explicit. |
| Write | 10 | nudge_act, nudge_dismiss, working_mode_set, cycle_mode_set, profile_correct, profile_delete, profile_flush, scout_decide, accommodation_confirm, accommodation_disable | Exposes bounded actions where the server-side Hapax API remains the authority. |
| Query (backend SSE) | 2 | query, query_refine | Collects backend query/refinement output into a single tool response. |
| Compound | 2 | status (health + gpu + infrastructure + working_mode), daily_summary (briefing + nudges + goals + drift) | Gives operator-facing summaries without requiring a client to reconstruct common views. |

`working_mode` and `working_mode_set` are canonical. `cycle_mode` and `cycle_mode_set` are deprecated aliases retained during the workspace-wide migration; both route through to `/working-mode` server-side. The MCP input schema accepts `research`, `rnd`, and `fortress`; a backend may accept a narrower set. Legacy `dev` / `prod` values are not accepted by this schema.

`chronicle` accepts filters `since`, `until`, `source`, `event_type`, `trace_id`, `limit`.
`chronicle_narrate` uses GET to request an LLM synthesis of a chronicle window
from the backend. Separately, `query` and `query_refine` POST to backend SSE
endpoints and can also invoke model work. Backend provider configuration and
usage costs apply to these model-backed operations.

## Install from source

Prerequisites: Python 3.12+, [uv](https://docs.astral.sh/uv/getting-started/installation/),
Git, and access to an existing Logos API deployment. Follow the backend
repository's setup instructions separately. `localhost` refers to the machine
running the MCP process; use the appropriate reachable URL if the API runs
elsewhere.

```bash
git clone https://github.com/hapax-systems/hapax-mcp.git
cd hapax-mcp
uv sync --locked
uv run hapax-mcp
```

The last command starts a stdio MCP process, which waits for protocol input;
it does not open an HTTP service or an interactive prompt. Normally your MCP
client launches this command for you. A successful launch does not prove API
connectivity. After registration, call `health` to check the configured backend;
if it reports a connection failure, check that API's service and `LOGOS_BASE_URL`.

As observed on September 24, 2026, the [GitHub release list](https://github.com/hapax-systems/hapax-mcp/releases)
was empty and the PyPI project lookup for `hapax-mcp` returned 404. The source
metadata version is `0.1.0`; the installation path documented here uses this
repository and its lockfile.

Dependencies: `mcp>=1.26`, `httpx>=0.28.1`, `pydantic>=2.0`. Entry point:
`hapax_mcp.server:main` (see [pyproject.toml](pyproject.toml)).

## Register in Claude Code

From the project where you want to use the tools, register the local process
with an absolute path to your clone:

```bash
claude mcp add --env LOGOS_BASE_URL=http://localhost:8051/api \
  --transport stdio --scope local hapax \
  -- uv --directory /absolute/path/to/hapax-mcp run hapax-mcp
```

Inspect the saved registration and MCP connection from that same project:

```bash
claude mcp get hapax
```

A connected MCP process still needs a successful `health` tool response to
establish backend connectivity.

Claude Code's local scope is private to that project. For shared project
configuration, use `.mcp.json`; MCP server entries do not belong in
`~/.claude/settings.json`. See the [Claude Code MCP documentation](https://code.claude.com/docs/en/mcp)
for scopes and client configuration.

Other stdio clients need the same `uv` command, arguments, and environment.
Their configuration and approval behavior must be checked separately. To target
an officium deployment as well, register a second instance with a distinct name
and its `LOGOS_BASE_URL`.

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `LOGOS_BASE_URL` | `http://localhost:8051/api` | Logos API base URL |
| `LOGOS_API_KEY` | unset | Optional bearer token; sent as `Authorization: Bearer …` if set |
| `COCKPIT_BASE_URL` | unset | Backward-compatible fallback for `LOGOS_BASE_URL` |
| `COCKPIT_API_KEY` | unset | Backward-compatible fallback for `LOGOS_API_KEY` |

The HTTP client sends a bearer token only when `LOGOS_API_KEY` (or its legacy
fallback) is set. This does not establish whether a particular backend requires
authentication. Supply credentials through your deployment's secret mechanism;
do not commit them to client configuration.

## Limits and errors

These limits come from [client.py](src/hapax_mcp/client.py) and
[server.py](src/hapax_mcp/server.py). To recheck the registered inventory and
configured limits from your checkout without calling the backend, run the
[source verification commands](CLAUDE.md#verify-the-source).

- Standard requests use an HTTPX timeout of 15 seconds. SSE requests use a
  120-second HTTPX timeout and a 30-second wait for each next line; these are
  not a total stream-duration deadline.
- JSON-formatted tool results are truncated after 50,000 characters, so large
  results may no longer be valid JSON. Query tools collect SSE text and stop
  after reaching 1,000 chunks or 1 MiB of accumulated text. The last chunk can
  cross the byte threshold; the response includes a truncation notice.
- URL path segments are validated against `[a-zA-Z0-9_-]+`.
- Tools format handled HTTP status, connection, and timeout errors as text.
  Validation and other unhandled failures may surface as MCP tool errors.
  Compound tools can return individual endpoint errors inside their result.

## Project layout

```
src/hapax_mcp/
  server.py      MCP server, 38 tool definitions
  client.py      HTTP client, env var contract, timeouts
  models/        Pydantic response models (health, infrastructure, profile, working_mode)
tests/           pytest suite (test_tools.py, test_response_models.py)
pyproject.toml   Package metadata, entry point, deps
```

The server emits a static instruction warning that tool output may include content from external sources and should not be treated as instructions. The warning is guidance to the client, not a content-sanitization or authorization guarantee.

## CI

| Workflow | Trigger | Effect |
|----------|---------|--------|
| `ci.yml` | push main, PR | ruff check + format, pyright, pytest, gitleaks, bandit; `all-green` aggregate |
| `auto-fix.yml` | CI failure on PR | Claude Code attempts a fix; max 3 attempts per branch |
| `claude-review.yml` | PR open / sync | Claude Code review on the PR |
| `dependabot-auto-merge.yml` | Dependabot PR | Auto-merge for patch / minor bumps |

## Related Repositories

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
