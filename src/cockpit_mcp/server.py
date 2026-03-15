"""Cockpit MCP server — exposes hapax cockpit API as Claude Code tools."""

from __future__ import annotations

import json
import logging

import httpx
from mcp.server.fastmcp import FastMCP

from cockpit_mcp import client

logger = logging.getLogger(__name__)

mcp = FastMCP(
    "cockpit",
    instructions="Hapax system cockpit — health, drift, profile, nudges, agents, GPU, and more.",
)


def _fmt_error(e: Exception) -> str:
    """Format an HTTP/connection error into a user-facing string."""
    if isinstance(e, httpx.HTTPStatusError):
        return f"HTTP {e.response.status_code}: {e.response.text[:200]}"
    if isinstance(e, httpx.ConnectError):
        return f"Connection failed: {e}"
    if isinstance(e, (httpx.TimeoutException, TimeoutError)):
        return f"Timeout: {e}"
    return f"Error: {e}"


# ── Read-only tools ─────────────────────────────────────────────────────────


@mcp.tool()
async def health() -> str:
    """Get current system health status (healthy/degraded/failed with check details)."""
    logger.debug("tool: health")
    try:
        return json.dumps(await client.get("/health"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("health failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def health_history() -> str:
    """Get health check history (recent entries with timestamps and failed checks)."""
    logger.debug("tool: health_history")
    try:
        return json.dumps(await client.get("/health/history"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("health_history failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def briefing() -> str:
    """Get the daily system briefing (last 24h summary)."""
    logger.debug("tool: briefing")
    try:
        return json.dumps(await client.get("/briefing"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("briefing failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def scout() -> str:
    """Get scout horizon scan — technology recommendations (adopt/evaluate/defer)."""
    logger.debug("tool: scout")
    try:
        return json.dumps(await client.get("/scout"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("scout failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def scout_decisions() -> str:
    """Get history of scout adoption decisions."""
    logger.debug("tool: scout_decisions")
    try:
        return json.dumps(await client.get("/scout/decisions"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("scout_decisions failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def drift() -> str:
    """Get drift report — divergence between intended and actual system state."""
    logger.debug("tool: drift")
    try:
        return json.dumps(await client.get("/drift"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("drift failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def cost() -> str:
    """Get LLM cost tracking data."""
    logger.debug("tool: cost")
    try:
        return json.dumps(await client.get("/cost"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("cost failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def goals() -> str:
    """Get active goals and their status."""
    logger.debug("tool: goals")
    try:
        return json.dumps(await client.get("/goals"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("goals failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def nudges() -> str:
    """Get active nudges (actionable suggestions from agents)."""
    logger.debug("tool: nudges")
    try:
        return json.dumps(await client.get("/nudges"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("nudges failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def agents() -> str:
    """List all agents with their status and descriptions."""
    logger.debug("tool: agents")
    try:
        return json.dumps(await client.get("/agents"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("agents failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def gpu() -> str:
    """Get GPU usage (VRAM, temperature, utilization)."""
    logger.debug("tool: gpu")
    try:
        return json.dumps(await client.get("/gpu"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("gpu failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def infrastructure() -> str:
    """Get infrastructure status (Docker containers, systemd timers)."""
    logger.debug("tool: infrastructure")
    try:
        return json.dumps(await client.get("/infrastructure"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("infrastructure failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def cycle_mode() -> str:
    """Get current cycle mode (dev or prod) and when it was last switched."""
    logger.debug("tool: cycle_mode")
    try:
        return json.dumps(await client.get("/cycle-mode"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("cycle_mode failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def profile() -> str:
    """Get operator profile summary (dimensions, fact counts, completeness)."""
    logger.debug("tool: profile")
    try:
        return json.dumps(await client.get("/profile"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("profile failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def profile_dimension(dimension: str) -> str:
    """Get detailed facts for a specific profile dimension.

    Args:
        dimension: Profile dimension name (e.g. 'work_style', 'communication', 'technical_preferences')
    """
    logger.debug("tool: profile_dimension dimension=%s", dimension)
    try:
        return json.dumps(await client.get(f"/profile/{dimension}"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("profile_dimension failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def profile_pending() -> str:
    """Get pending profile facts awaiting flush."""
    logger.debug("tool: profile_pending")
    try:
        return json.dumps(await client.get("/profile/facts/pending"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("profile_pending failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def accommodations() -> str:
    """Get active accommodations (system adaptations based on operator profile)."""
    logger.debug("tool: accommodations")
    try:
        return json.dumps(await client.get("/accommodations"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("accommodations failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def copilot() -> str:
    """Get copilot observation message (contextual suggestion based on current state)."""
    logger.debug("tool: copilot")
    try:
        return json.dumps(await client.get("/copilot"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("copilot failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def readiness() -> str:
    """Get system readiness assessment."""
    logger.debug("tool: readiness")
    try:
        return json.dumps(await client.get("/readiness"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("readiness failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def workspace() -> str:
    """Get workspace analysis (screen, camera, hardware state)."""
    logger.debug("tool: workspace")
    try:
        return json.dumps(await client.get("/workspace"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("workspace failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def manual() -> str:
    """Get the system manual content."""
    logger.debug("tool: manual")
    try:
        return json.dumps(await client.get("/manual"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("manual failed: %s", e)
        return _fmt_error(e)


# ── Write tools ─────────────────────────────────────────────────────────────


@mcp.tool()
async def nudge_act(source_id: str) -> str:
    """Execute a nudge's recommended action.

    Args:
        source_id: The nudge source ID to act on
    """
    logger.debug("tool: nudge_act source_id=%s", source_id)
    try:
        return json.dumps(await client.post(f"/nudges/{source_id}/act"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("nudge_act failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def nudge_dismiss(source_id: str) -> str:
    """Dismiss a nudge without acting on it.

    Args:
        source_id: The nudge source ID to dismiss
    """
    logger.debug("tool: nudge_dismiss source_id=%s", source_id)
    try:
        return json.dumps(await client.post(f"/nudges/{source_id}/dismiss"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("nudge_dismiss failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def cycle_mode_set(mode: str) -> str:
    """Switch cycle mode between dev and prod.

    Args:
        mode: Target mode — 'dev' or 'prod'
    """
    logger.debug("tool: cycle_mode_set mode=%s", mode)
    try:
        return json.dumps(await client.put("/cycle-mode", {"mode": mode}), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("cycle_mode_set failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def profile_correct(dimension: str, key: str, value: str) -> str:
    """Correct a profile fact.

    Args:
        dimension: Profile dimension name
        key: Fact key to correct
        value: New value for the fact
    """
    logger.debug("tool: profile_correct dimension=%s key=%s", dimension, key)
    try:
        return json.dumps(
            await client.post(
                "/profile/correct", {"dimension": dimension, "key": key, "value": value}
            ),
            indent=2,
        )
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("profile_correct failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def profile_delete(dimension: str, key: str) -> str:
    """Delete a profile fact.

    Args:
        dimension: Profile dimension name
        key: Fact key to delete
    """
    logger.debug("tool: profile_delete dimension=%s key=%s", dimension, key)
    try:
        return json.dumps(
            await client.post("/profile/delete", {"dimension": dimension, "key": key}),
            indent=2,
        )
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("profile_delete failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def profile_flush() -> str:
    """Flush pending profile facts into the operator profile."""
    logger.debug("tool: profile_flush")
    try:
        return json.dumps(await client.post("/profile/facts/flush"), indent=2)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("profile_flush failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def scout_decide(component: str, decision: str, notes: str = "") -> str:
    """Record a decision on a scout recommendation.

    Args:
        component: Component name from scout report
        decision: One of 'adopted', 'deferred', 'dismissed'
        notes: Optional notes explaining the decision
    """
    logger.debug("tool: scout_decide component=%s decision=%s", component, decision)
    try:
        return json.dumps(
            await client.post(
                f"/scout/{component}/decide", {"decision": decision, "notes": notes}
            ),
            indent=2,
        )
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("scout_decide failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def accommodation_confirm(accommodation_id: str) -> str:
    """Confirm and activate an accommodation.

    Args:
        accommodation_id: The accommodation ID to confirm
    """
    logger.debug("tool: accommodation_confirm id=%s", accommodation_id)
    try:
        return json.dumps(
            await client.post(f"/accommodations/{accommodation_id}/confirm"), indent=2
        )
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("accommodation_confirm failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def accommodation_disable(accommodation_id: str) -> str:
    """Disable an active accommodation.

    Args:
        accommodation_id: The accommodation ID to disable
    """
    logger.debug("tool: accommodation_disable id=%s", accommodation_id)
    try:
        return json.dumps(
            await client.post(f"/accommodations/{accommodation_id}/disable"), indent=2
        )
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("accommodation_disable failed: %s", e)
        return _fmt_error(e)


# ── SSE-consuming tools ─────────────────────────────────────────────────────


@mcp.tool()
async def query(question: str) -> str:
    """Ask a natural language question about the system (uses RAG + agent pipeline).

    Args:
        question: Natural language question about the system
    """
    logger.debug("tool: query question=%s", question[:80])
    try:
        return await client.post_sse("/query/run", {"query": question})
    except (
        httpx.HTTPStatusError,
        httpx.ConnectError,
        httpx.TimeoutException,
        TimeoutError,
    ) as e:
        logger.error("query failed: %s", e)
        return _fmt_error(e)


@mcp.tool()
async def query_refine(question: str, prior_result: str, agent_type: str) -> str:
    """Refine a previous query result with a follow-up question.

    Args:
        question: Follow-up question
        prior_result: The result from the previous query
        agent_type: Agent type to use for refinement
    """
    logger.debug("tool: query_refine question=%s", question[:80])
    try:
        return await client.post_sse(
            "/query/refine",
            {"query": question, "prior_result": prior_result, "agent_type": agent_type},
        )
    except (
        httpx.HTTPStatusError,
        httpx.ConnectError,
        httpx.TimeoutException,
        TimeoutError,
    ) as e:
        logger.error("query_refine failed: %s", e)
        return _fmt_error(e)


# ── Compound tools ──────────────────────────────────────────────────────────


@mcp.tool()
async def status() -> str:
    """Get combined system status: health + GPU + infrastructure + cycle mode."""
    logger.debug("tool: status")
    results = {}
    for name, path in [
        ("health", "/health"),
        ("gpu", "/gpu"),
        ("infrastructure", "/infrastructure"),
        ("cycle_mode", "/cycle-mode"),
    ]:
        try:
            results[name] = await client.get(path)
        except Exception as e:
            logger.error("status/%s failed: %s", name, e)
            results[name] = {"error": str(e)}
    return json.dumps(results, indent=2)


@mcp.tool()
async def daily_summary() -> str:
    """Get combined daily summary: briefing + nudges + goals + drift."""
    logger.debug("tool: daily_summary")
    results = {}
    for name, path in [
        ("briefing", "/briefing"),
        ("nudges", "/nudges"),
        ("goals", "/goals"),
        ("drift", "/drift"),
    ]:
        try:
            results[name] = await client.get(path)
        except Exception as e:
            logger.error("daily_summary/%s failed: %s", name, e)
            results[name] = {"error": str(e)}
    return json.dumps(results, indent=2)


# ── Entry point ─────────────────────────────────────────────────────────────


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
