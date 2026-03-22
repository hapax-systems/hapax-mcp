# hapax-mcp

MCP server bridging the hapax cockpit API to Claude Code. Exposes 34 tools (21 read-only, 9 write, 2 streaming, 2 compound) for system health, profile management, agent control, and natural language queries.

## Installation

```bash
uv sync
```

## Usage

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "cockpit": {
      "command": "uv",
      "args": ["--directory", "/path/to/hapax-mcp", "run", "hapax-mcp"],
      "env": {
        "COCKPIT_BASE_URL": "http://localhost:8051/api"
      }
    }
  }
}
```

## Part of the Hapax Research Project

Infrastructure for a research project implementing Clark & Brennan's (1991) conversational grounding theory in a voice AI system. Bridges cockpit APIs to Claude Code. See [hapax-council](https://github.com/ryanklee/hapax-council) for the research context.

| Repository | Role |
|-----------|------|
| [hapax-council](https://github.com/ryanklee/hapax-council) | Primary research artifact — voice daemon, grounding system, experiment infrastructure |
| [hapax-constitution](https://github.com/ryanklee/hapax-constitution) | Governance specification — axioms, implications, canons |
| [hapax-officium](https://github.com/ryanklee/hapax-officium) | Supporting software — management decision support |
| [hapax-watch](https://github.com/ryanklee/hapax-watch) | Research instrument — Wear OS biometric companion |
| **hapax-mcp** (this repo) | Infrastructure — MCP server for Claude Code |

## License

Apache 2.0 — see [LICENSE](LICENSE).
