"""
Workload Template API.

This module provides a service-based interface for managing workload templates in EGS.
Workload templates define reusable configurations for deploying workloads.

Usage:
    >>> import egs
    >>> from egs.workload_template import workloadTemplate
    >>>
    >>> # Authenticate first
    >>> egs.authenticate(endpoint="https://api.example.com", api_key="your-key")
    >>>
    >>> # Create a workload template
    >>> from egs.workload_template import CreateWorkloadTemplateRequest, Step, StepType
    >>> request = CreateWorkloadTemplateRequest(
    ...     name="my-template",
    ...     burstDuration="1h",
    ...     deletionPolicy="Delete",
    ...     clusterNames=["cluster-1"],
    ...     steps=[Step(name="deploy", type=StepType.HELM)],
    ...     helmConfigs=[...],
    ... )
    >>> response = workloadTemplate.create(request)
    >>>
    >>> # List all templates
    >>> templates = workloadTemplate.list()
    >>>
    >>> # Get a specific template
    >>> template = workloadTemplate.get(name="my-template")
    >>>
    >>> # Update a template
    >>> from egs.workload_template import UpdateWorkloadTemplateRequest
    >>> update = UpdateWorkloadTemplateRequest(burstDuration="2h")
    >>> workloadTemplate.update(name="my-template", request=update)
    >>>
    >>> # Delete a template
    >>> workloadTemplate.delete(name="my-template")
"""

# Service interface and implementation
from egs.internal.workload_template.workload_template_service import (
    IWorkloadTemplateService,
    WorkloadTemplate,
    workloadTemplate,
)

# Types
from egs.internal.workload_template.workload_template_types import (
    CreateWorkloadTemplateRequest,
    CreateWorkloadTemplateResponse,
    DeleteWorkloadTemplateResponse,
    GetWorkloadTemplateResponse,
    ListWorkloadTemplateResponse,
    UpdateWorkloadTemplateRequest,
    UpdateWorkloadTemplateResponse,
    WorkloadTemplateItem,
)

# Re-export shared types from workload_placement for convenience
from egs.internal.workload_placement.workload_placement_types import (
    CmdExec,
    DeletionPolicy,
    HelmConfig,
    HelmFlags,
    ManifestResource,
    SecretRef,
    Step,
    StepType,
    YamlValues,
)

__all__ = [
    # Service
    "workloadTemplate",
    "IWorkloadTemplateService",
    "WorkloadTemplate",
    # Request
    "CreateWorkloadTemplateRequest",
    "UpdateWorkloadTemplateRequest",
    # Response
    "CreateWorkloadTemplateResponse",
    "DeleteWorkloadTemplateResponse",
    "GetWorkloadTemplateResponse",
    "ListWorkloadTemplateResponse",
    "UpdateWorkloadTemplateResponse",
    "WorkloadTemplateItem",
    # Shared Types
    "Step",
    "StepType",
    "DeletionPolicy",
    "HelmConfig",
    "HelmFlags",
    "SecretRef",
    "ManifestResource",
    "YamlValues",
    "CmdExec",
]
