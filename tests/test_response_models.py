"""Tests for MCP response models — consumer-side contract validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from hapax_mcp.models import (
    GpuResponse,
    HealthResponse,
    InfrastructureResponse,
    ProfileDimensionResponse,
    ProfileResponse,
    WorkingModeResponse,
)


class TestHealthResponse:
    def test_valid(self):
        data = {
            "overall_status": "degraded",
            "total_checks": 105,
            "healthy": 102,
            "degraded": 3,
            "failed": 0,
            "failed_checks": ["systemd.drift"],
            "timestamp": "2026-03-23T21:40:24Z",
        }
        m = HealthResponse.model_validate(data)
        assert m.overall_status == "degraded"
        assert m.total_checks == 105

    def test_extra_fields_allowed(self):
        data = {
            "overall_status": "healthy",
            "total_checks": 10,
            "healthy": 10,
            "degraded": 0,
            "failed": 0,
            "failed_checks": [],
            "duration_ms": 500,
            "new_field": True,
        }
        m = HealthResponse.model_validate(data)
        assert m.healthy == 10

    def test_missing_required_raises(self):
        data = {"overall_status": "healthy", "total_checks": 10}
        with pytest.raises(ValidationError):
            HealthResponse.model_validate(data)


class TestGpuResponse:
    def test_valid(self):
        data = {
            "name": "RTX 3090",
            "total_mb": 24576,
            "used_mb": 7079,
            "free_mb": 17497,
            "usage_pct": 28.8,
            "loaded_models": ["nomic-embed-text-v2-moe:latest"],
        }
        m = GpuResponse.model_validate(data)
        assert m.name == "RTX 3090"
        assert m.usage_pct == 28.8

    def test_missing_name_raises(self):
        data = {"total_mb": 24576, "used_mb": 7079, "free_mb": 17497, "usage_pct": 28.8}
        with pytest.raises(ValidationError):
            GpuResponse.model_validate(data)


class TestInfrastructureResponse:
    def test_valid(self):
        data = {
            "containers": [
                {"name": "grafana", "service": "grafana", "state": "running", "health": "healthy"}
            ]
        }
        m = InfrastructureResponse.model_validate(data)
        assert len(m.containers) == 1
        assert m.containers[0].name == "grafana"

    def test_empty_containers(self):
        data = {"containers": []}
        m = InfrastructureResponse.model_validate(data)
        assert m.containers == []

    def test_missing_containers_raises(self):
        with pytest.raises(ValidationError):
            InfrastructureResponse.model_validate({})


class TestWorkingModeResponse:
    def test_valid(self):
        data = {"mode": "rnd", "switched_at": "2026-03-23T20:19:50Z"}
        m = WorkingModeResponse.model_validate(data)
        assert m.mode == "rnd"

    def test_missing_mode_raises(self):
        data = {"switched_at": "2026-03-23T20:19:50Z"}
        with pytest.raises(ValidationError):
            WorkingModeResponse.model_validate(data)


class TestProfileResponse:
    def test_valid(self):
        data = {
            "dimensions": [
                {"name": "identity", "fact_count": 11, "summary": "Operator profile..."},
                {"name": "values", "fact_count": 87},
            ]
        }
        m = ProfileResponse.model_validate(data)
        assert len(m.dimensions) == 2
        assert m.dimensions[0].name == "identity"

    def test_missing_dimensions_raises(self):
        with pytest.raises(ValidationError):
            ProfileResponse.model_validate({})


class TestProfileDimensionResponse:
    def test_valid_with_facts(self):
        data = {"name": "identity", "summary": "...", "facts": [{"key": "role", "value": "eng"}]}
        m = ProfileDimensionResponse.model_validate(data)
        assert m.name == "identity"
        assert len(m.facts) == 1

    def test_valid_without_facts(self):
        data = {"name": "identity"}
        m = ProfileDimensionResponse.model_validate(data)
        assert m.facts is None
