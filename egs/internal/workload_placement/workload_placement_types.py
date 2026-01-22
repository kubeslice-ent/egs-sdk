"""
Workload Placement Types.

Contains all Pydantic models for workload placement requests and responses.
"""

import re
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator
from pydantic.functional_validators import field_validator

# ============================================================================
# Utility Functions
# ============================================================================

DURATION_PATTERN = re.compile(r"^(?:(\d+d)?(\d+h)?(\d+m)?)$")


def validate_duration(value: str, field_name: str, allow_zero: bool = False) -> str:
    """Validate duration string format and optionally check for non-zero value."""
    if not value:
        return value

    if not DURATION_PATTERN.match(value):
        raise ValueError(
            f'"{field_name}" must match pattern like "1d2h30m", "2h", "30m"'
        )

    if not allow_zero:
        numbers = re.findall(r"\d+", value)
        total = sum(int(n) for n in numbers) if numbers else 0
        if total == 0:
            raise ValueError(f'"{field_name}" cannot be zero')

    return value


# ============================================================================
# Enums
# ============================================================================


class StepType(str, Enum):
    HELM = "helm"
    MANIFEST = "manifest"
    COMMAND = "command"


class DeletionPolicy(str, Enum):
    DELETE = "Delete"
    RETAIN = "Retain"


# ============================================================================
# Shared Models (Used in both Request and Response)
# ============================================================================


class Step(BaseModel):
    """Step configuration - used in both request and response."""

    name: str
    type: StepType


class HelmFlags(BaseModel):
    """Helm deployment flags."""

    createNamespace: Optional[bool] = None
    wait: Optional[bool] = None
    atomic: Optional[bool] = None
    skipCRDs: Optional[bool] = None
    cleanupOnFail: Optional[bool] = None
    timeout: Optional[str] = None


class SecretRef(BaseModel):
    """Secret reference."""

    name: str


# ============================================================================
# Request Models - YAML Utility
# ============================================================================


class YamlValues(BaseModel):
    """
    Accepts either a YAML string or a Python dict,
    and always normalizes to a dict for internal use.
    """

    values: Union[Dict[str, Any], str] = Field(default_factory=dict)

    @field_validator("values", mode="before")
    @classmethod
    def parse_values(cls, v: Union[str, Dict[str, Any], None]) -> Dict[str, Any]:
        if v is None:
            return {}
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                parsed = yaml.safe_load(v)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML: {e}")
            if parsed is None:
                return {}
            if not isinstance(parsed, dict):
                raise ValueError("YAML must be a mapping (key-value pairs)")
            return dict(parsed)
        raise TypeError("values must be a dict or YAML string")  # type: ignore[unreachable]

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """Serialize directly to the inner dict (flatten the wrapper)."""
        return self.values


# ============================================================================
# Request Models - Helm (with YAML parsing for values)
# ============================================================================


class HelmConfig(BaseModel):
    """Helm configuration for request - values accepts YamlValues with dict or YAML string."""

    name: str
    chart: str
    releaseName: str
    releaseNamespace: str
    repoName: str
    repoURL: str
    secretRef: Optional[SecretRef] = None
    values: Optional[YamlValues] = None
    version: Optional[str] = None
    helmFlags: Optional[HelmFlags] = None


# ============================================================================
# Request Models - Manifest
# ============================================================================


class ManifestResource(BaseModel):
    """Manifest resource wrapper - manifest accepts YamlValues with dict or YAML string."""

    name: str
    manifest: YamlValues


# ============================================================================
# Request Models - Command
# ============================================================================


class CmdExec(BaseModel):
    """Command execution configuration."""

    name: str
    cmd: str


# ============================================================================
# Request Models - GPR Details (with validation)
# ============================================================================


class GprDetails(BaseModel):
    """GPR details for request - with strict validation."""

    memoryPerGpu: int = Field(..., ge=1)
    enableAutoGpuSelection: bool
    numberOfGPUs: int = Field(..., ge=1)
    numberOfGPUNodes: int = Field(..., ge=1)
    instanceType: Optional[str] = None
    gpuShape: Optional[str] = None
    exitDuration: str
    priority: int

    @field_validator("exitDuration")
    @classmethod
    def validate_exit_duration(cls, v: str) -> str:
        return validate_duration(v, "exitDuration", allow_zero=False)

    @model_validator(mode="after")
    def validate_gpu_selection_fields(self) -> "GprDetails":
        if self.enableAutoGpuSelection:
            if self.instanceType is not None:
                raise ValueError(
                    "instanceType must not be provided when enableAutoGpuSelection is True"
                )
            if self.gpuShape is not None:
                raise ValueError(
                    "gpuShape must not be provided when enableAutoGpuSelection is True"
                )
        else:
            if self.instanceType is None:
                raise ValueError(
                    "instanceType is required when enableAutoGpuSelection is False"
                )
            if self.gpuShape is None:
                raise ValueError(
                    "gpuShape is required when enableAutoGpuSelection is False"
                )
        return self


# ============================================================================
# Request Models - Main Request
# ============================================================================


class CreateWorkloadPlacementRequest(BaseModel):
    """Request model for creating a workload placement."""

    workspaceName: str
    name: str
    clusterNames: List[str] = Field(..., min_length=1)
    steps: List[Step] = Field(..., min_length=1)
    numPlacements: Optional[int] = None
    burstDuration: Optional[str] = None
    deletionPolicy: Optional[DeletionPolicy] = None
    helmConfigs: Optional[List[HelmConfig]] = None
    manifestResources: Optional[List[ManifestResource]] = None
    cmdExec: Optional[List[CmdExec]] = None
    gprDetails: Optional[GprDetails] = None
    workloadTemplateName: Optional[str] = None
    serviceAccountName: Optional[str] = None
    enableBurst: Optional[bool] = None
    enableEGS: Optional[bool] = None

    @field_validator("burstDuration")
    @classmethod
    def validate_burst_duration(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return v
        return validate_duration(v, "burstDuration", allow_zero=False)

    @model_validator(mode="after")
    def validate_at_least_one_config(self) -> "CreateWorkloadPlacementRequest":
        if not any([self.helmConfigs, self.manifestResources, self.cmdExec]):
            raise ValueError(
                "At least one of 'helmConfigs', 'manifestResources', or 'cmdExec' must be provided"
            )
        return self


# ============================================================================
# Response Models - GPR Status (response-only, runtime data)
# ============================================================================


class GprStatusResponse(BaseModel):
    """GPR provisioning status in cluster placement decision."""

    gprName: Optional[str] = None
    gprType: Optional[str] = None
    gpuShape: Optional[str] = None
    instanceType: Optional[str] = None
    memoryPerGpu: Optional[int] = None
    numberOfGPUNodes: Optional[int] = None
    provisioningStatus: Optional[str] = None
    startTime: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class StepResultResponse(BaseModel):
    """Result of a deployment step execution."""

    name: str = ""
    type: str = ""
    success: bool = False
    message: Optional[str] = None
    duration: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class ConditionResponse(BaseModel):
    """Kubernetes-style condition status."""

    type: str = ""
    status: str = ""
    reason: Optional[str] = None
    message: Optional[str] = None
    lastTransitionTime: Optional[str] = None
    observedGeneration: Optional[int] = None

    model_config = ConfigDict(extra="allow")


class ManifestIdentifierResponse(BaseModel):
    """Manifest resource identifier."""

    kind: str = ""
    name: str = ""
    resource: Optional[str] = None
    version: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class ManifestConditionResponse(BaseModel):
    """Manifest apply condition."""

    identifier: Optional[ManifestIdentifierResponse] = None

    model_config = ConfigDict(extra="allow")


class ClusterPlacementDecisionResponse(BaseModel):
    """Cluster placement decision with status details."""

    clusterName: str = ""
    phase: Optional[str] = None
    message: Optional[str] = None
    currentStep: Optional[int] = None
    startTime: Optional[str] = None
    workloadPlacementName: Optional[str] = None
    conditions: List[ConditionResponse] = Field(default_factory=list)
    stepResults: List[StepResultResponse] = Field(default_factory=list)
    manifestConditions: List[ManifestConditionResponse] = Field(default_factory=list)
    gprStatus: Optional[GprStatusResponse] = None

    model_config = ConfigDict(extra="allow")


class WorkloadPlacementStatusResponse(BaseModel):
    """Overall workload placement status."""

    placementStatus: Optional[str] = None
    observedClusterNames: List[str] = Field(default_factory=list)
    clusterPlacementDecisions: List[ClusterPlacementDecisionResponse] = Field(
        default_factory=list
    )

    model_config = ConfigDict(extra="allow")


# ============================================================================
# Response Models - Lenient versions for API responses
# ============================================================================


class GprDetailsResponse(BaseModel):
    """GPR details in response - lenient, all optional."""

    enableAutoGpuSelection: Optional[bool] = None
    exitDuration: Optional[str] = None
    memoryPerGpu: Optional[int] = None
    numberOfGPUNodes: Optional[int] = None
    numberOfGPUs: Optional[int] = None
    priority: Optional[int] = None
    requeueOnFailure: Optional[bool] = None
    instanceType: Optional[str] = None
    gpuShape: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class HelmConfigResponse(BaseModel):
    """Helm configuration in response - values as raw dict."""

    name: str = ""
    chart: str = ""
    releaseName: str = ""
    releaseNamespace: str = ""
    repoName: str = ""
    repoURL: str = ""
    values: Optional[Dict[str, Any]] = None
    version: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class ManifestResourceResponse(BaseModel):
    """Manifest resource in response - manifest as raw dict."""

    name: str = ""
    manifest: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


# ============================================================================
# Response Models - Main (reusing WorkloadPlacementItem for get/list)
# ============================================================================


class CreateWorkloadPlacementResponse(BaseModel):
    """Response after creating a workload placement."""

    name: str = ""

    model_config = ConfigDict(extra="allow")

    @classmethod
    def from_api_response(
        cls, data: Dict[str, Any]
    ) -> "CreateWorkloadPlacementResponse":
        return cls(**data)


class WorkloadPlacementItem(BaseModel):
    """
    Workload placement data - used in both list response and get response.
    This is the canonical representation of a workload placement from the API.
    """

    name: str = ""
    workspaceName: str = ""
    clusterNames: List[str] = Field(default_factory=list)
    numPlacements: Optional[int] = None
    deletionPolicy: Optional[str] = None
    enableEGS: Optional[bool] = None
    enableRedistribute: Optional[bool] = None
    workloadTemplateName: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    status: Optional[WorkloadPlacementStatusResponse] = None
    gprDetails: Optional[GprDetailsResponse] = None
    helmConfigs: List[HelmConfigResponse] = Field(default_factory=list)
    manifestResources: List[ManifestResourceResponse] = Field(default_factory=list)
    steps: List[Step] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")


class GetWorkloadPlacementResponse(BaseModel):
    """Response after getting a workload placement - returns full placement data."""

    name: str = ""
    workspaceName: str = ""
    clusterNames: List[str] = Field(default_factory=list)
    numPlacements: Optional[int] = None
    deletionPolicy: Optional[str] = None
    enableEGS: Optional[bool] = None
    enableRedistribute: Optional[bool] = None
    workloadTemplateName: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    status: Optional[WorkloadPlacementStatusResponse] = None
    gprDetails: Optional[GprDetailsResponse] = None
    helmConfigs: List[HelmConfigResponse] = Field(default_factory=list)
    manifestResources: List[ManifestResourceResponse] = Field(default_factory=list)
    steps: List[Step] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "GetWorkloadPlacementResponse":
        """Create response from API response data."""
        return cls(**data)


class ListWorkloadPlacementResponse(BaseModel):
    """Response after listing workload placements."""

    placements: List[WorkloadPlacementItem] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow")

    @classmethod
    def from_api_response(cls, data: Any) -> "ListWorkloadPlacementResponse":
        if isinstance(data, list):
            placements = [WorkloadPlacementItem(**p) for p in data]
            return cls(placements=placements)
        raw_placements = data.get("placements", []) if isinstance(data, dict) else []
        placements = [WorkloadPlacementItem(**p) for p in raw_placements]
        return cls(placements=placements)


class DeleteWorkloadPlacementResponse(BaseModel):
    """Response after deleting a workload placement (data is empty {})."""

    name: str = ""

    model_config = ConfigDict(extra="allow")

    @classmethod
    def from_api_response(cls, name: str) -> "DeleteWorkloadPlacementResponse":
        """Create response with the deleted workload placement name."""
        return cls(name=name)


class UpdateWorkloadPlacementRequest(BaseModel):
    """Request model for updating a workload placement (helmConfigs and manifestResources)."""

    name: str
    helmConfigs: Optional[List[HelmConfig]] = None
    manifestResources: Optional[List[ManifestResource]] = None

    @model_validator(mode="after")
    def validate_at_least_one(self) -> "UpdateWorkloadPlacementRequest":
        """At least one of helmConfigs or manifestResources must be provided."""
        if not self.helmConfigs and not self.manifestResources:
            raise ValueError(
                "At least one of 'helmConfigs' or 'manifestResources' must be provided"
            )
        return self


class UpdateWorkloadPlacementResponse(BaseModel):
    """Response after updating a workload placement (data is empty {})."""

    name: str = ""

    model_config = ConfigDict(extra="allow")

    @classmethod
    def from_api_response(cls, name: str) -> "UpdateWorkloadPlacementResponse":
        """Create response with the updated workload placement name."""
        return cls(name=name)


class EnableEGSRequest(BaseModel):
    """Request model for enabling/disabling EGS on a workload placement."""

    enableEGS: bool

    model_config = ConfigDict(extra="allow")


class EnableEGSResponse(BaseModel):
    """Response after enabling/disabling EGS on a workload placement."""

    name: str = ""

    model_config = ConfigDict(extra="allow")

    @classmethod
    def from_api_response(cls, name: str) -> "EnableEGSResponse":
        """Create response with the workload placement name."""
        return cls(name=name)
