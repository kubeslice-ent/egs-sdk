from typing import List, Optional

import egs
from egs.authenticated_session import AuthenticatedSession
from egs.exceptions import BadParameters, ResourceNotFound, UnhandledException
from egs.internal.workspace_policy.workspace_policy_types import (
    GetWorkspacePolicyResponse,
    ListWorkspacePolicyResponse,
    UpdateWorkspacePolicyRequest,
    UpdateWorkspacePolicyResponse,
)


def list_workspace_policies(
    *,
    authenticated_session: Optional[AuthenticatedSession] = None,
) -> ListWorkspacePolicyResponse:
    """List all workspace policies."""
    auth = egs.get_authenticated_session(authenticated_session)
    api_response = auth.client.invoke_sdk_operation("/api/v1/workspace-policies", "GET")
    if api_response.status_code != 200:
        raise UnhandledException(**api_response.data)
    return ListWorkspacePolicyResponse(**api_response.data)


def get_workspace_policy(
    *,
    policy_name: str,
    authenticated_session: Optional[AuthenticatedSession] = None,
) -> GetWorkspacePolicyResponse:
    """Get a specific workspace policy by workspace name."""
    auth = egs.get_authenticated_session(authenticated_session)
    api_response = auth.client.invoke_sdk_operation(
        f"/api/v1/workspace-policies/{policy_name}", "GET"
    )
    print(api_response)
    if api_response.status_code == 404:
        raise ResourceNotFound(
            api_response, resource_type="Workspace Policy", resource_id=policy_name
        )
    elif api_response.status_code != 200:
        raise UnhandledException(api_response)
    return GetWorkspacePolicyResponse(**api_response.data)


def update_workspace_policy(
    *,
    policy_name: str,
    priorityRange: Optional[str] = None,
    maxGPRs: Optional[int] = None,
    maxExitDurationPerGPR: Optional[str] = None,
    enforceIdleTimeOut: Optional[bool] = None,
    requeueOnFailure: Optional[bool] = None,
    enableAutoEviction: Optional[bool] = None,
    gpuShapes: Optional[List[str]] = None,
    maxGpuPerGpr: Optional[int] = None,
    maxMemoryPerGpr: Optional[int] = None,
    authenticated_session: Optional[AuthenticatedSession] = None,
) -> UpdateWorkspacePolicyResponse:
    """Update a workspace policy."""
    auth = egs.get_authenticated_session(authenticated_session)
    req = UpdateWorkspacePolicyRequest(
        priorityRange=priorityRange,
        maxGPRs=maxGPRs,
        maxExitDurationPerGPR=maxExitDurationPerGPR,
        enforceIdleTimeOut=enforceIdleTimeOut,
        requeueOnFailure=requeueOnFailure,
        enableAutoEviction=enableAutoEviction,
        gpuShapes=gpuShapes,
        maxGpuPerGpr=maxGpuPerGpr,
        maxMemoryPerGpr=maxMemoryPerGpr,
    )
    api_response = auth.client.invoke_sdk_operation(
        f"/api/v1/workspace-policies/{policy_name}", "PUT", req
    )
    if api_response.status_code == 404:
        raise ResourceNotFound(
            api_response, resource_type="Workspace Policy", resource_id=policy_name
        )
    elif api_response.status_code == 400:
        raise BadParameters(api_response)
    elif api_response.status_code != 200:
        raise UnhandledException(api_response)
    return UpdateWorkspacePolicyResponse(**api_response.data)
