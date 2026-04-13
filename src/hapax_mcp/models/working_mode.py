"""Response model for the working_mode endpoint."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class WorkingModeResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    mode: str
    switched_at: str
