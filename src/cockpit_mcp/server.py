"""Cockpit MCP server — exposes hapax cockpit API as Claude Code tools."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from cockpit_mcp import client

mcp = FastMCP("cockpit", instructions="Hapax system cockpit — health, drift, profile, nudges, agents, GPU, and more.")


# ── Read-only tools ─────────────────────────────────────────────────────────


@mcp.tool()
async def health() -> str:
    """Get current system health status (healthy/degraded/failed with check details)."""
    return json.dumps(await client.get("/health"), indent=2)


@mcp.tool()
async def health_history() -> str:
    """Get health check history (recent entries with timestamps and failed checks)."""
    return json.dumps(await client.get("/health/history"), indent=2)


@mcp.tool()
async def briefing() -> str:
    """Get the daily system briefing (last 24h summary)."""
    return json.dumps(await client.get("/briefing"), indent=2)


@mcp.tool()
async def scout() -> str:
    """Get scout horizon scan — technology recommendations (adopt/evaluate/defer)."""
    return json.dumps(await client.get("/scout"), indent=2)


@mcp.tool()
async def scout_decisions() -> str:
    """Get history of scout adoption decisions."""
    return json.dumps(await client.get("/scout/decisions"), indent=2)


@mcp.tool()
async def drift() -> str:
    """Get drift report — divergence between intended and actual system state."""
    return json.dumps(await client.get("/drift"), indent=2)


@mcp.tool()
async def cost() -> str:
    """Get LLM cost tracking data."""
    return json.dumps(await client.get("/cost"), indent=2)


@mcp.tool()
async def goals() -> str:
    """Get active goals and their status."""
    return json.dumps(await client.get("/goals"), indent=2)


@mcp.tool()
async def nudges() -> str:
    """Get active nudges (actionable suggestions from agents)."""
    return json.dumps(await client.get("/nudges"), indent=2)


@mcp.tool()
async def agents() -> str:
    """List all agents with their status and descriptions."""
    return json.dumps(await client.get("/agents"), indent=2)


@mcp.tool()
async def gpu() -> str:
    """Get GPU usage (VRAM, temperature, utilization)."""
    return json.dumps(await client.get("/gpu"), indent=2)


@mcp.tool()
async def infrastructure() -> str:
    """Get infrastructure status (Docker containers, systemd timers)."""
    return json.dumps(await client.get("/infrastructure"), indent=2)


@mcp.tool()
async def cycle_mode() -> str:
    """Get current cycle mode (dev or prod) and when it was last switched."""
    return json.dumps(await client.get("/cycle-mode"), indent=2)


@mcp.tool()
async def profile() -> str:
    """Get operator profile summary (dimensions, fact counts, completeness)."""
    return json.dumps(await client.get("/profile"), indent=2)


@mcp.tool()
async def profile_dimension(dimension: str) -> str:
    """Get detailed facts for a specific profile dimension.

    Args:
        dimension: Profile dimension name (e.g. 'work_style', 'communication', 'technical_preferences')
    """
    return json.dumps(await client.get(f"/profile/{dimension}"), indent=2)


@mcp.tool()
async def profile_pending() -> str:
    """Get pending profile facts awaiting flush."""
    return json.dumps(await client.get("/profile/facts/pending"), indent=2)


@mcp.tool()
async def accommodations() -> str:
    """Get active accommodations (system adaptations based on operator profile)."""
    return json.dumps(await client.get("/accommodations"), indent=2)


@mcp.tool()
async def copilot() -> str:
    """Get copilot observation message (contextual suggestion based on current state)."""
    return json.dumps(await client.get("/copilot"), indent=2)


@mcp.tool()
async def readiness() -> str:
    """Get system readiness assessment."""
    return json.dumps(await client.get("/readiness"), indent=2)


@mcp.tool()
async def workspace() -> str:
    """Get workspace analysis (screen, camera, hardware state)."""
    return json.dumps(await client.get("/workspace"), indent=2)


@mcp.tool()
async def manual() -> str:
    """Get the system manual content."""
    return json.dumps(await client.get("/manual"), indent=2)


# ── Write tools ─────────────────────────────────────────────────────────────


@mcp.tool()
async def nudge_act(source_id: str) -> str:
    """Execute a nudge's recommended action.

    Args:
        source_id: The nudge source ID to act on
    """
    return json.dumps(await client.post(f"/nudges/{source_id}/act"), indent=2)


@mcp.tool()
async def nudge_dismiss(source_id: str) -> str:
    """Dismiss a nudge without acting on it.

    Args:
        source_id: The nudge source ID to dismiss
    """
    return json.dumps(await client.post(f"/nudges/{source_id}/dismiss"), indent=2)


@mcp.tool()
async def cycle_mode_set(mode: str) -> str:
    """Switch cycle mode between dev and prod.

    Args:
        mode: Target mode — 'dev' or 'prod'
    """
    return json.dumps(await client.put("/cycle-mode", {"mode": mode}), indent=2)


@mcp.tool()
async def profile_correct(dimension: str, key: str, value: str) -> str:
    """Correct a profile fact.

    Args:
        dimension: Profile dimension name
        key: Fact key to correct
        value: New value for the fact
    """
    return json.dumps(
        await client.post("/profile/correct", {"dimension": dimension, "key": key, "value": value}),
        indent=2,
    )


@mcp.tool()
async def profile_delete(dimension: str, key: str) -> str:
    """Delete a profile fact.

    Args:
        dimension: Profile dimension name
        key: Fact key to delete
    """
    return json.dumps(
        await client.post("/profile/delete", {"dimension": dimension, "key": key}),
        indent=2,
    )


@mcp.tool()
async def profile_flush() -> str:
    """Flush pending profile facts into the operator profile."""
    return json.dumps(await client.post("/profile/facts/flush"), indent=2)


@mcp.tool()
async def scout_decide(component: str, decision: str, notes: str = "") -> str:
    """Record a decision on a scout recommendation.

    Args:
        component: Component name from scout report
        decision: One of 'adopted', 'deferred', 'dismissed'
        notes: Optional notes explaining the decision
    """
    return json.dumps(
        await client.post(f"/scout/{component}/decide", {"decision": decision, "notes": notes}),
        indent=2,
    )


@mcp.tool()
async def accommodation_confirm(accommodation_id: str) -> str:
    """Confirm and activate an accommodation.

    Args:
        accommodation_id: The accommodation ID to confirm
    """
    return json.dumps(await client.post(f"/accommodations/{accommodation_id}/confirm"), indent=2)


@mcp.tool()
async def accommodation_disable(accommodation_id: str) -> str:
    """Disable an active accommodation.

    Args:
        accommodation_id: The accommodation ID to disable
    """
    return json.dumps(await client.post(f"/accommodations/{accommodation_id}/disable"), indent=2)


# ── SSE-consuming tools ─────────────────────────────────────────────────────


@mcp.tool()
async def query(question: str) -> str:
    """Ask a natural language question about the system (uses RAG + agent pipeline).

    Args:
        question: Natural language question about the system
    """
    return await client.post_sse("/query/run", {"query": question})


@mcp.tool()
async def query_refine(question: str, prior_result: str, agent_type: str) -> str:
    """Refine a previous query result with a follow-up question.

    Args:
        question: Follow-up question
        prior_result: The result from the previous query
        agent_type: Agent type to use for refinement
    """
    return await client.post_sse(
        "/query/refine",
        {"query": question, "prior_result": prior_result, "agent_type": agent_type},
    )


# ── Compound tools ──────────────────────────────────────────────────────────


@mcp.tool()
async def status() -> str:
    """Get combined system status: health + GPU + infrastructure + cycle mode."""
    results = {}
    for name, path in [("health", "/health"), ("gpu", "/gpu"), ("infrastructure", "/infrastructure"), ("cycle_mode", "/cycle-mode")]:
        try:
            results[name] = await client.get(path)
        except Exception as e:
            results[name] = {"error": str(e)}
    return json.dumps(results, indent=2)


@mcp.tool()
async def daily_summary() -> str:
    """Get combined daily summary: briefing + nudges + goals + drift."""
    results = {}
    for name, path in [("briefing", "/briefing"), ("nudges", "/nudges"), ("goals", "/goals"), ("drift", "/drift")]:
        try:
            results[name] = await client.get(path)
        except Exception as e:
            results[name] = {"error": str(e)}
    return json.dumps(results, indent=2)


# ── Entry point ─────────────────────────────────────────────────────────────


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
