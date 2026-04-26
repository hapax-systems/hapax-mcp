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
- Constitution: https://github.com/ryanklee/hapax-constitution

## Inter-repo position

MCP bridge. Consumes the council and officium logos APIs over HTTP and presents 36 tools to Claude Code. The MCP ecosystem norm is MIT; this repo carries MIT explicitly per operator divergence (every other runtime repo is PolyForm Strict).

<!-- hapax-sdlc:preamble:end -->
<!-- hapax-sdlc:preamble:end -->


# hapax-mcp

Infrastructure for a research project implementing Clark & Brennan's (1991) conversational grounding theory in a production voice AI system. See [hapax-council](https://github.com/ryanklee/hapax-council) for the primary research artifact and experiment design.

## Role in the research project

The research apparatus is developed and operated through Claude Code as the primary interactive interface (Tier 1 in the three-tier agent architecture). This MCP server bridges the logos APIs (council on `:8051`, officium on `:8050`) to Claude Code via the Model Context Protocol, exposing 34 tools for system health, profile management, agent control, and natural language queries.

## Configuration

Add to `~/.claude/settings.json`:

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

## Tools

**Read-only (21):** health, health_history, briefing, scout, scout_decisions, drift, cost, goals, nudges, agents, gpu, infrastructure, cycle_mode, profile, profile_dimension, profile_pending, accommodations, copilot, readiness, workspace, manual

**Write (9):** nudge_act, nudge_dismiss, cycle_mode_set, profile_correct, profile_delete, profile_flush, scout_decide, accommodation_confirm, accommodation_disable

**Streaming (2):** query, query_refine (SSE)

**Compound (2):** `status` (health + gpu + infrastructure + cycle_mode), `daily_summary` (briefing + nudges + goals + drift)

## Ecosystem

| Repository | Role |
|-----------|------|
| [hapax-council](https://github.com/ryanklee/hapax-council) | Primary research artifact — voice daemon, grounding system, experiment infrastructure |
| [hapax-constitution](https://github.com/ryanklee/hapax-constitution) | Governance specification — axioms, implications, canons, precedents |
| [hapax-officium](https://github.com/ryanklee/hapax-officium) | Supporting software — management decision support |
| [hapax-watch](https://github.com/ryanklee/hapax-watch) | Research instrument — Wear OS biometric companion |
| **hapax-mcp** (this repo) | Infrastructure — MCP server for Claude Code |

## License

Apache 2.0 — see [LICENSE](LICENSE).
