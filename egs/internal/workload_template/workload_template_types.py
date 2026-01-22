"""
Workload Template Types.

Contains Pydantic models for workload template requests and responses.
Reuses shared types from workload_placement where applicable.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Reuse shared types from workload_placement
from egs.internal.workload_placement.workload_placement_types import (
    CmdExec,
    DeletionPolicy,
    HelmConfig,
    HelmConfigResponse,
    HelmFlags,
    ManifestResource,
    ManifestResourceResponse,
    SecretRef,
    Step,
    YamlValues,
    validate_duration,
)


# ============================================================================
# Request Models
# ============================================================================

class CreateWorkloadTemplateRequest(BaseModel):
    """Request model for creating a workload template."""
    name: str
    burstDuration: str
    deletionPolicy: DeletionPolicy
    clusterNames: List[str] = Field(..., min_length=1)
    steps: List[Step] = Field(..., min_length=1)
    helmConfigs: Optional[List[HelmConfig]] = None
    manifestResources: Optional[List[ManifestResource]] = None
    cmdExec: Optional[List[CmdExec]] = None
    serviceAccount: Optional[str] = None
    enableBurst: Optional[bool] = None
    autoPlacement: Optional[bool] = None

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def validate_burst_duration(self) -> "CreateWorkloadTemplateRequest":
        """Validate burstDuration is not zero."""
        validate_duration(self.burstDuration, "burstDuration", allow_zero=False)
        return self

    @model_validator(mode="after")
    def validate_at_least_one_config(self) -> "CreateWorkloadTemplateRequest":
        """At least one of helmConfigs, manifestResources, or cmdExec must be provided."""
        if not any([self.helmConfigs, self.manifestResources, self.cmdExec]):
            raise ValueError(
                "At least one of 'helmConfigs', 'manifestResources', or 'cmdExec' must be provided"
            )
        return self


class UpdateWorkloadTemplateRequest(BaseModel):
    """Request model for updating a workload template (name is passed via URL path)."""
    burstDuration: Optional[str] = None
    deletionPolicy: Optional[DeletionPolicy] = None
    clusterNames: Optional[List[str]] = None
    steps: Optional[List[Step]] = None
    helmConfigs: Optional[List[HelmConfig]] = None
    manifestResources: Optional[List[ManifestResource]] = None
    cmdExec: Optional[List[CmdExec]] = None
    serviceAccount: Optional[str] = None
    enableBurst: Optional[bool] = None
    autoPlacement: Optional[bool] = None

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def validate_burst_duration(self) -> "UpdateWorkloadTemplateRequest":
        """Validate burstDuration if provided."""
        if self.burstDuration:
            validate_duration(self.burstDuration, "burstDuration", allow_zero=False)
        return self


# ============================================================================
# Response Models
# ============================================================================

class CreateWorkloadTemplateResponse(BaseModel):
    """Response after creating a workload template."""
    name: str = ""

    model_config = ConfigDict(extra="allow")

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "CreateWorkloadTemplateResponse":
        """Create response from API response data."""
        if isinstance(data, dict):
            return cls(**data)
        return cls(name=str(data) if data else "")


class WorkloadTemplateItem(BaseModel):
    """A single workload template item - used in list and get responses."""
    name: str = ""
    burstDuration: Optional[str] = None
    deletionPolicy: Optional[str] = None
    clusterNames: List[str] = Field(default_factory=list)
    serviceAccount: Optional[str] = None
    enableBurst: Optional[bool] = None
    autoPlacement: Optional[bool] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    helmConfigs: List[HelmConfigResponse] = Field(default_factory=list)
    manifestResources: List[ManifestResourceResponse] = Field(default_factory=list)
    steps: List[Step] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class GetWorkloadTemplateResponse(BaseModel):
    """Response after getting a workload template."""
    name: str = ""
    burstDuration: Optional[str] = None
    deletionPolicy: Optional[str] = None
    clusterNames: List[str] = Field(default_factory=list)
    serviceAccount: Optional[str] = None
    enableBurst: Optional[bool] = None
    autoPlacement: Optional[bool] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    helmConfigs: List[HelmConfigResponse] = Field(default_factory=list)
    manifestResources: List[ManifestResourceResponse] = Field(default_factory=list)
    steps: List[Step] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "GetWorkloadTemplateResponse":
        """Create response from API response data."""
        return cls(**data)


class ListWorkloadTemplateResponse(BaseModel):
    """Response after listing workload templates."""
    templates: List[WorkloadTemplateItem] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")

    @classmethod
    def from_api_response(cls, data: Any) -> "ListWorkloadTemplateResponse":
        """Create response from API response data."""
        if isinstance(data, list):
            templates = [WorkloadTemplateItem(**t) for t in data]
            return cls(templates=templates)
        raw_templates = data.get("templates", []) if isinstance(data, dict) else []
        templates = [WorkloadTemplateItem(**t) for t in raw_templates]
        return cls(templates=templates)


class UpdateWorkloadTemplateResponse(BaseModel):
    """Response after updating a workload template."""
    name: str = ""

    model_config = ConfigDict(extra="allow")

    @classmethod
    def from_api_response(cls, name: str) -> "UpdateWorkloadTemplateResponse":
        """Create response with the updated workload template name."""
        return cls(name=name)


class DeleteWorkloadTemplateResponse(BaseModel):
    """Response after deleting a workload template."""
    name: str = ""

    model_config = ConfigDict(extra="allow")

    @classmethod
    def from_api_response(cls, name: str) -> "DeleteWorkloadTemplateResponse":
        """Create response with the deleted workload template name."""
        return cls(name=name)
