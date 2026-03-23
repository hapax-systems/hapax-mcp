"""Response models for logos API endpoints.

Consumer-side contracts: these models define what the MCP client requires
from the logos API. Extra fields are allowed (Postel's Law).
"""

from hapax_mcp.models.health import HealthCheckDetail, HealthHistoryEntry, HealthResponse
from hapax_mcp.models.infrastructure import (
    ContainerInfo,
    GpuResponse,
    InfrastructureResponse,
)
from hapax_mcp.models.profile import (
    ProfileDimensionResponse,
    ProfileResponse,
)
from hapax_mcp.models.working_mode import WorkingModeResponse

__all__ = [
    "ContainerInfo",
    "GpuResponse",
    "HealthCheckDetail",
    "HealthHistoryEntry",
    "HealthResponse",
    "InfrastructureResponse",
    "ProfileDimensionResponse",
    "ProfileResponse",
    "WorkingModeResponse",
]
