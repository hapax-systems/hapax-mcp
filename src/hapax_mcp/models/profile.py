"""Response models for profile endpoints."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ProfileDimensionSummary(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    fact_count: int


class ProfileResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    dimensions: list[ProfileDimensionSummary]


class ProfileDimensionResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    summary: str | None = None
    facts: list[dict] | None = None
