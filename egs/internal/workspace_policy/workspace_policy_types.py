from typing import List, Optional

from pydantic import BaseModel


class GlobalGPUConstraints(BaseModel):
    gpuShapes: List[str]
    maxGPUPerGpr: int
    maxMemoryPerGpr: int


class WorkspacePolicy(BaseModel):
    workspaceName: str
    PriorityRange: str
    maxGPRs: int
    maxExitDurationPerGPR: str
    requeueOnFailure: bool
    enableAutoEviction: bool
    globalGPUConstraints: Optional[GlobalGPUConstraints]


class GetWorkspacePolicyResponse(BaseModel):
    item: WorkspacePolicy


class UpdateWorkspacePolicyRequest(BaseModel):
    priorityRange: Optional[str] = None
    maxGPRs: Optional[int] = None
    maxExitDurationPerGPR: Optional[str] = None
    enforceIdleTimeOut: Optional[bool] = None
    requeueOnFailure: Optional[bool] = None
    enableAutoEviction: Optional[bool] = None
    gpuShapes: Optional[List[str]] = None
    maxGpuPerGpr: Optional[int] = None
    maxMemoryPerGpr: Optional[int] = None


class UpdateWorkspacePolicyResponse(BaseModel):
    item: WorkspacePolicy


class ListWorkspacePolicyResponse(BaseModel):
    items: List[WorkspacePolicy]
