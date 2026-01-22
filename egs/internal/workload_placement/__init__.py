"""Workload placement internal types and utilities."""

# Service
from egs.internal.workload_placement.workload_placement_service import (
    IWorkloadPlacementService,
    WorkloadPlacement,
    workloadPlacement,
)

# All types (Request and Response models)
from egs.internal.workload_placement.workload_placement_types import (
    # Enums
    DeletionPolicy,
    StepType,
    # Request - Utility
    YamlValues,
    # Request - Helm
    HelmConfig,
    HelmFlags,
    SecretRef,
    # Request - Manifest
    Manifest,
    ManifestMetadata,
    ManifestResource,
    # Request - Command
    CmdExec,
    # Request - Step
    Step,
    # Request - GPR
    GprDetails,
    # Request - Main
    CreateWorkloadPlacementRequest,
    UpdateWorkloadPlacementRequest,
    # Response - Nested
    ClusterPlacementDecisionResponse,
    ConditionResponse,
    GprDetailsResponse,
    GprStatusResponse,
    HelmConfigResponse,
    ManifestConditionResponse,
    ManifestIdentifierResponse,
    ManifestResourceResponse,
    StepResultResponse,
    WorkloadPlacementStatusResponse,
    # Response - Main
    CreateWorkloadPlacementResponse,
    DeleteWorkloadPlacementResponse,
    GetWorkloadPlacementResponse,
    ListWorkloadPlacementResponse,
    UpdateWorkloadPlacementResponse,
    WorkloadPlacementItem,
)

__all__ = [
    # Service
    "workloadPlacement",
    "IWorkloadPlacementService",
    "WorkloadPlacement",
    # Enums
    "StepType",
    "DeletionPolicy",
    # Request - Utility
    "YamlValues",
    # Request - Helm
    "HelmConfig",
    "HelmFlags",
    "SecretRef",
    # Request - Manifest
    "ManifestResource",
    "Manifest",
    "ManifestMetadata",
    # Request - Command
    "CmdExec",
    # Request - Step
    "Step",
    # Request - GPR
    "GprDetails",
    # Request - Main
    "CreateWorkloadPlacementRequest",
    "UpdateWorkloadPlacementRequest",
    # Response - Nested
    "ClusterPlacementDecisionResponse",
    "ConditionResponse",
    "GprDetailsResponse",
    "GprStatusResponse",
    "HelmConfigResponse",
    "ManifestConditionResponse",
    "ManifestIdentifierResponse",
    "ManifestResourceResponse",
    "StepResultResponse",
    "WorkloadPlacementStatusResponse",
    # Response - Main
    "CreateWorkloadPlacementResponse",
    "DeleteWorkloadPlacementResponse",
    "GetWorkloadPlacementResponse",
    "ListWorkloadPlacementResponse",
    "UpdateWorkloadPlacementResponse",
    "WorkloadPlacementItem",
]
