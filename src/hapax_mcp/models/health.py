"""Response models for health endpoints."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    overall_status: str
    total_checks: int
    healthy: int
    degraded: int
    failed: int
    failed_checks: list[str]


class HealthCheckDetail(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    status: str


class HealthHistoryEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    timestamp: str
    overall_status: str
    total_checks: int
    failed_checks: list[str]
