"""Workload template internal types and utilities."""

# Service
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
]
