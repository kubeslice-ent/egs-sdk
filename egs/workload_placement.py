"""
Workload Placement API.

This module provides a service-based interface for managing workload placements in EGS.
Workload placements allow you to deploy Helm charts, Kubernetes manifests,
and execute commands on GPU-enabled clusters.

Usage:
    >>> import egs
    >>> from egs.workload_placement import workloadPlacement
    >>>
    >>> # Authenticate first
    >>> egs.authenticate(server_url="https://api.example.com", api_key="your-key")
    >>>
    >>> # Create a workload placement
    >>> from egs.workload_placement import CreateWorkloadPlacementRequest, Step, StepType
    >>> request = CreateWorkloadPlacementRequest(
    ...     workspaceName="my-workspace",
    ...     name="my-deployment",
    ...     clusterNames=["cluster-1"],
    ...     steps=[Step(name="deploy", type=StepType.HELM)],
    ...     helmConfigs=[...],
    ... )
    >>> response = workloadPlacement.create(request)
    >>>
    >>> # List all placements
    >>> placements = workloadPlacement.list()
    >>>
    >>> # List placements by workspace
    >>> placements = workloadPlacement.list_by_workspace(workspace_name="pizza")
    >>>
    >>> # Get a specific placement
    >>> placement = workloadPlacement.get(name="my-deployment")
    >>>
    >>> # Update helm configs or manifest resources
    >>> workloadPlacement.update(name="my-deployment", helm_configs=[...])
    >>>
    >>> # Delete a placement
    >>> workloadPlacement.delete(name="my-deployment")
"""

# Service interface and implementation
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
    # Request models
    CmdExec,
    CreateWorkloadPlacementRequest,
    EnableEGSRequest,
    GprDetails,
    HelmConfig,
    HelmFlags,
    Manifest,
    ManifestMetadata,
    ManifestResource,
    SecretRef,
    Step,
    UpdateWorkloadPlacementRequest,
    YamlValues,
    # Response models
    CreateWorkloadPlacementResponse,
    DeleteWorkloadPlacementResponse,
    EnableEGSResponse,
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
    # Request
    "CreateWorkloadPlacementRequest",
    "UpdateWorkloadPlacementRequest",
    "EnableEGSRequest",
    # Response
    "CreateWorkloadPlacementResponse",
    "ListWorkloadPlacementResponse",
    "GetWorkloadPlacementResponse",
    "UpdateWorkloadPlacementResponse",
    "DeleteWorkloadPlacementResponse",
    "EnableEGSResponse",
    "WorkloadPlacementItem",
    # Shared Types
    "Step",
    "StepType",
    "DeletionPolicy",
    "HelmConfig",
    "HelmFlags",
    "SecretRef",
    "YamlValues",
    "ManifestResource",
    "Manifest",
    "ManifestMetadata",
    "CmdExec",
    "GprDetails",
]
