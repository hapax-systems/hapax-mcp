<!-- hapax-sdlc:preamble:begin -->
<!-- hapax-public:surface=github.repo.hapax-mcp.readme.preamble:begin -->

# hapax-mcp

`hapax-mcp` is an integration bridge in the **Hapax Research Lab** portfolio ([hapaxresearch.com](https://hapaxresearch.com)). It is maintained for MCP integration and inspection, not as a general-purpose framework.

## Reader promise

Experimental MCP stdio bridge exposing Logos HTTP API state and bounded actions to Claude Code and compatible MCP clients.

## Reader value

Lets compatible MCP clients inspect state and invoke bounded endpoints against a running Logos API while keeping policy and authorization in the underlying backend.

## Claim ceiling

Experimental integration bridge only; requires an existing Logos API deployment, supplies no independent authorization layer, and is not a general-purpose MCP framework.

## License and rights

MIT-licensed integration bridge for MCP clients; requires a separately running Logos API backend and is not a general-purpose MCP framework.

Rendered summary: MIT. See `LICENSE`, `NOTICE.md`, `CITATION.cff`, and `.zenodo.json` for the authority surfaces.

## Public boundary

- Issues are redirect-only; no discussions, no pull requests accepted; see `CONTRIBUTING.md` and `SUPPORT.md`
- Published by **Hapax Research Lab** (`hrl-han`, [hapaxresearch.com](https://hapaxresearch.com)). Legal entity (as filed): Hapax Research LLC, organized in Wyoming on 2026-05-10, filing ID 2026-001973400.
- Security disclosures and factual correction proposals: `hrl-han@hapaxresearch.com` (see `SECURITY.md` and [hapaxresearch.com/about/#contact](https://hapaxresearch.com/about/#contact)). The network commits to receipt, retention and published correction. It promises no response time.
- Public copy uses `hapax-systems` organization links for first-party repositories; README text is orientation rather than a live runtime receipt.
- Governance reference: https://github.com/hapax-systems/hapax-constitution

## Portfolio position

Logos MCP Bridge. Translates MCP stdio tool calls into HTTP requests against a separately running Logos API deployment while keeping policy and authorization in the underlying backend.

<!-- hapax-public:surface=github.repo.hapax-mcp.readme.preamble:end -->
<!-- hapax-sdlc:preamble:end -->

## Overview

`hapax-mcp` is an experimental FastMCP (`stdio` transport) bridge developed by **Hapax Research Lab** that translates MCP tool calls into HTTP requests against a **separately running Logos API deployment**. Installing this repository installs only the local `stdio` bridge; it does not install, configure, or start a Logos backend runtime.

By default, `hapax-mcp` targets `http://localhost:8051/api`. Set `LOGOS_BASE_URL` (for example `http://localhost:8050/api`) to target an alternative Logos API instance. Available endpoints and accepted parameters depend on the backend version and configuration; tool registration alone does not establish backend compatibility.

This bridge provides neither an independent authorization policy nor a read-only mode: write tools are registered alongside inspection tools. The operator authorizes client tool invocations, and the configured backend API remains responsible for enforcing access and action policy.

## Tool Surface (38 Registered Tools)

Defined in [src/hapax_mcp/server.py](src/hapax_mcp/server.py), including two deprecated aliases retained for backward compatibility:

| Group | Count | Tools | Purpose |
|---|---|---|---|
| Inspection (GET) | 22 | `health`, `health_history`, `briefing`, `scout`, `scout_decisions`, `drift`, `cost`, `goals`, `nudges`, `agents`, `gpu`, `infrastructure`, `profile`, `profile_dimension`, `profile_pending`, `accommodations`, `copilot`, `readiness`, `workspace`, `manual`, `working_mode`, `cycle_mode` | Inspects backend state over HTTP GET without transferring state ownership to the MCP client. |
| Chronicle | 2 | `chronicle`, `chronicle_narrate` | Queries filtered event history (`since`, `until`, `source`, `event_type`, `trace_id`, `limit`) or requests a backend narrative synthesis. |
| Write | 10 | `nudge_act`, `nudge_dismiss`, `working_mode_set`, `cycle_mode_set`, `profile_correct`, `profile_delete`, `profile_flush`, `scout_decide`, `accommodation_confirm`, `accommodation_disable` | Invokes bounded state-change endpoints governed by the backend API. |
| Query (backend SSE) | 2 | `query`, `query_refine` | Streams backend query or refinement SSE output and returns a consolidated tool response. |
| Compound | 2 | `status` (`health` + `gpu` + `infrastructure` + `working_mode`), `daily_summary` (`briefing` + `nudges` + `goals` + `drift`) | Aggregates common multi-endpoint status views into single calls. |

`working_mode` and `working_mode_set` are canonical; `cycle_mode` and `cycle_mode_set` are deprecated aliases routing to `/working-mode`. The MCP input schema accepts `research`, `rnd`, and `fortress` (individual backends may accept a narrower subset; legacy `dev` / `prod` values are rejected).

`chronicle_narrate`, `query`, and `query_refine` can trigger model inference on the backend; backend provider configuration and usage limits apply.

## Install from Source

Prerequisites: Python 3.12+, [uv](https://docs.astral.sh/uv/getting-started/installation/), Git, and network reachability to a running Logos API instance.

```bash
git clone https://github.com/hapax-systems/hapax-mcp.git
cd hapax-mcp
uv sync --locked
uv run hapax-mcp
```

`uv run hapax-mcp` launches a `stdio` JSON-RPC process intended to be spawned by an MCP client rather than used as an interactive CLI. After registering the server in your client, invoke the `health` tool to verify connectivity to `LOGOS_BASE_URL`.

Dependencies: `mcp>=1.26`, `httpx>=0.28.1`, `pydantic>=2.0`. Entry point: `hapax_mcp.server:main` ([pyproject.toml](pyproject.toml)).

## Register in Claude Code

From the project directory where you want the tools available, register the local `stdio` server using an absolute checkout path:

```bash
claude mcp add --env LOGOS_BASE_URL=http://localhost:8051/api \
  --transport stdio --scope local hapax \
  -- uv --directory /absolute/path/to/hapax-mcp run hapax-mcp
```

Verify the saved client registration:

```bash
claude mcp get hapax
```

For shared project configuration, use `.mcp.json` rather than `~/.claude/settings.json`; see the [Claude Code MCP documentation](https://code.claude.com/docs/en/mcp). To bridge a second Logos API deployment simultaneously, register a second instance under a distinct server name and `LOGOS_BASE_URL`.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `LOGOS_BASE_URL` | `http://localhost:8051/api` | Target Logos API base URL |
| `LOGOS_API_KEY` | unset | Optional bearer token sent as `Authorization: Bearer ...` when set |
| `COCKPIT_BASE_URL` | unset | Legacy fallback when `LOGOS_BASE_URL` is unset |
| `COCKPIT_API_KEY` | unset | Legacy fallback when `LOGOS_API_KEY` is unset |

Provide credentials through your environment's secret store; never commit API keys to configuration files.

## Limits and Error Handling

Configured in [src/hapax_mcp/client.py](src/hapax_mcp/client.py) and [src/hapax_mcp/server.py](src/hapax_mcp/server.py) (verifiable offline via [CLAUDE.md](CLAUDE.md#verify-the-source)):

- **Timeouts:** 15s HTTPX timeout for standard requests; 120s HTTPX timeout and 30s per-line wait on SSE streams.
- **Truncation:** JSON tool responses truncate after 50,000 characters (truncated payloads may not parse as complete JSON). SSE collection stops after 1,000 chunks or 1 MiB of accumulated text.
- **Input validation:** Dynamic URL path segments are validated against `[a-zA-Z0-9_-]+`.
- **Errors:** Handled HTTP status, connection, and timeout errors are formatted into readable text via `_fmt_error()`. Unhandled validation failures surface as MCP tool errors, and compound tools report per-endpoint failures inline.
- **Untrusted output warning:** The server instructs clients that tool responses may contain external text and must not be treated as instructions.

## Project Layout

```
src/hapax_mcp/
  server.py      MCP server and 38 tool definitions
  client.py      HTTP/SSE client, environment contract, timeouts
  models/        Pydantic response models (health, infrastructure, profile, working_mode)
tests/           pytest suite (test_tools.py, test_response_models.py)
pyproject.toml   Package metadata, entry point, dependencies
```

## Continuous Integration

| Workflow | Trigger | Checks |
|---|---|---|
| `ci.yml` | push to `main`, pull request | `ruff check`, `ruff format --check`, `pyright`, `pytest`, `gitleaks`, `bandit`, and required `all-green` gate |
| `semgrep.yml` | push to `main`, pull request, schedule | Static analysis (`semgrep ci`) |
| `dependabot-auto-merge.yml` | Dependabot PR | Automated merge for passing patch/minor dependency updates |

## Related Hapax Research Lab Surfaces

| Surface | Role |
|---|---|
| [hapaxresearch.com](https://hapaxresearch.com) | Hapax Research Lab portal, research records, commitments register, and contact policy |
| [reins](https://github.com/hapax-systems/reins) | Terminal cockpit for observing and previewing governed AI-agent delivery lifecycles (BSL 1.1) |
| [hapax-constitution](https://github.com/hapax-systems/hapax-constitution) | Constitutional governance specification and `hapax-sdlc` enforcement tooling |
| [hapax-spine](https://github.com/hapax-systems/hapax-spine) | Source-available runtime mechanism behind Reins (BSL 1.1) |
| [hapax-research-ledger](https://github.com/hapax-systems/hapax-research-ledger) | Public-domain numeric evidence ledger (CC0-1.0) |

## License

MIT — see [LICENSE](LICENSE).

---

*HACA-C v0.3.15, the lab's draft rule for labelling machine-made text, not an external certification. No request to a natural person to approve the final wording, and no such approval, was found in hrl-han's sending, review and coordination records when the text was released. hrl-han releases a text once its checking is complete, under a standing rule that hrl-han's principal, who is not named in this text, adopted before the text was drafted. Review record: https://hapaxresearch.com/review-record/ (open to anyone). This label records how the text was made; it does not certify that the text is true. An unaltered record can contain false claims or miss relevant events.*
