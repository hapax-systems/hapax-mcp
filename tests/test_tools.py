"""Tool-level tests for hapax_mcp.server.

These tests stub the httpx client and verify each working_mode tool routes
to the correct endpoint with the correct body. Closes audit findings F12+F13.

Uses asyncio.run() directly instead of pytest-asyncio (not in dev deps).
"""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, patch

import pytest


def run(coro):
    """Run an async tool function in a fresh event loop."""
    return asyncio.run(coro)


@pytest.fixture
def mock_get():
    """Patch hapax_mcp.client.get to return a fixed mode response."""
    with patch("hapax_mcp.server.client.get", new=AsyncMock()) as mock:
        mock.return_value = {"mode": "rnd", "switched_at": "2026-04-13T00:00:00+00:00"}
        yield mock


@pytest.fixture
def mock_put():
    """Patch hapax_mcp.client.put to record calls and return the new mode."""
    with patch("hapax_mcp.server.client.put", new=AsyncMock()) as mock:

        async def _put(path, body):
            return {"mode": body["mode"], "switched_at": "2026-04-13T00:00:00+00:00"}

        mock.side_effect = _put
        yield mock


@pytest.fixture
def mock_get_validated():
    """Patch get_validated for the compound `status` tool."""
    with patch("hapax_mcp.server.client.get_validated", new=AsyncMock()) as mock:
        from hapax_mcp.models import (
            GpuResponse,
            HealthResponse,
            InfrastructureResponse,
            WorkingModeResponse,
        )

        async def _get_validated(path, model):
            if model is HealthResponse:
                return HealthResponse(
                    overall_status="healthy",
                    total_checks=10,
                    healthy=10,
                    degraded=0,
                    failed=0,
                    failed_checks=[],
                )
            if model is GpuResponse:
                return GpuResponse(
                    name="NVIDIA RTX 3090",
                    total_mb=24576,
                    used_mb=12000,
                    free_mb=12576,
                    usage_pct=48.8,
                )
            if model is InfrastructureResponse:
                return InfrastructureResponse(containers=[])
            if model is WorkingModeResponse:
                return WorkingModeResponse(mode="rnd", switched_at="2026-04-13T00:00:00+00:00")
            raise AssertionError(f"unexpected model: {model}")

        mock.side_effect = _get_validated
        yield mock


def test_working_mode_calls_working_mode_endpoint(mock_get):
    from hapax_mcp.server import working_mode

    run(working_mode())
    mock_get.assert_called_once_with("/working-mode")


def test_cycle_mode_aliases_working_mode(mock_get):
    from hapax_mcp.server import cycle_mode, working_mode

    # Both tools should hit the same endpoint.
    run(cycle_mode())
    run(working_mode())
    assert mock_get.call_count == 2
    for call in mock_get.call_args_list:
        assert call.args == ("/working-mode",)


def test_working_mode_set_routes_research(mock_put):
    from hapax_mcp.server import working_mode_set

    run(working_mode_set("research"))
    mock_put.assert_called_once_with("/working-mode", {"mode": "research"})


def test_working_mode_set_routes_rnd(mock_put):
    from hapax_mcp.server import working_mode_set

    run(working_mode_set("rnd"))
    mock_put.assert_called_once_with("/working-mode", {"mode": "rnd"})


def test_cycle_mode_set_aliases_working_mode_set(mock_put):
    from hapax_mcp.server import cycle_mode_set, working_mode_set

    run(cycle_mode_set("research"))
    run(working_mode_set("rnd"))
    assert mock_put.call_count == 2
    # Both tools route to /working-mode under the hood.
    for call in mock_put.call_args_list:
        assert call.args[0] == "/working-mode"


def test_status_includes_both_working_mode_and_cycle_mode_keys(mock_get_validated):
    """The compound `status` tool emits both keys for backward compat (F12)."""
    from hapax_mcp.server import status

    result_str = run(status())
    result = json.loads(result_str)

    # The canonical key.
    assert "working_mode" in result
    assert result["working_mode"]["mode"] == "rnd"

    # The deprecated alias key — present, identical value.
    assert "cycle_mode" in result
    assert result["cycle_mode"] == result["working_mode"]
