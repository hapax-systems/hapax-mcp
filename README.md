# cockpit-mcp

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
      "args": ["--directory", "/path/to/cockpit-mcp", "run", "cockpit-mcp"],
      "env": {
        "COCKPIT_BASE_URL": "http://localhost:8051/api"
      }
    }
  }
}
```

## Related

- [hapax-council](https://github.com/ryanklee/hapax-council) — Personal operating environment (cockpit API on :8051)
- [hapax-officium](https://github.com/ryanklee/hapax-officium) — Management decision support (cockpit API on :8050)
