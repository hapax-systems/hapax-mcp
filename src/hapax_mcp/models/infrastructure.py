"""Response models for infrastructure and GPU endpoints."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class GpuResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    total_mb: int
    used_mb: int
    free_mb: int
    usage_pct: float


class ContainerInfo(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    service: str
    state: str
    health: str


class InfrastructureResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    containers: list[ContainerInfo]
