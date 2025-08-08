from typing import List, Optional

import egs
from egs.authenticated_session import AuthenticatedSession
from egs.exceptions import GpuAlreadyProvisioned, GpuAlreadyReleased, UnhandledException
from egs.internal.gpr.create_gpr_data import CreateGprRequest, CreateGprResponse
from egs.internal.gpr.delete_gpr_data import DeleteGprRequest, DeleteGprResponse
from egs.internal.gpr.gpr_release_data import GprReleaseRequest
from egs.internal.gpr.gpr_status_data import (
    GpuRequestData,
    WorkspaceGpuRequestDataResponse,
)
from egs.internal.gpr.update_gpr_name_data import UpdateGprNameRequest
from egs.internal.gpr.update_gpr_priority_data import UpdateGprPriorityRequest


def request_gpu(
    request_name: str,
    workspace_name: str,
    node_count: int,
    gpu_per_node_count: int,
    memory_per_gpu: int,
    exit_duration: str,
    priority: int,
    idle_timeout_duration: str,
    enforce_idle_timeout: bool,
    enable_auto_gpu_selection: bool = False,
    enable_auto_cluster_selection: bool = False,
    cluster_name: str = "",
    instance_type: str = "",
    gpu_shape: str = "",
    requeue_on_failure: Optional[bool] = None,
    enable_eviction: Optional[bool] = None,
    preferred_clusters: Optional[List[str]] = None,
    authenticated_session: Optional[AuthenticatedSession] = None,
) -> str:
    auth = egs.get_authenticated_session(authenticated_session)
    req = CreateGprRequest(
        request_name=request_name,
        workspace_name=workspace_name,
        cluster_name=cluster_name,
        node_count=node_count,
        preferred_clusters=preferred_clusters,
        enable_auto_cluster_selection=enable_auto_cluster_selection,
        enable_auto_gpu_selection=enable_auto_gpu_selection,
        gpu_per_node_count=gpu_per_node_count,
        memory_per_gpu=memory_per_gpu,
        instance_type=instance_type,
        gpu_shape=gpu_shape,
        exit_duration=exit_duration,
        priority=priority,
        idle_timeout_duration=idle_timeout_duration,
        enforce_idle_timeout=enforce_idle_timeout,
        enable_eviction=enable_eviction,
        requeue_on_failure=requeue_on_failure,
    )
    print(f"Request: {req}\n")
    api_response = auth.client.invoke_sdk_operation("/api/v1/gpr", "POST", req)
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return CreateGprResponse(**api_response.data).gpr_id


def cancel_gpu_request(
    request_id: str, authenticated_session: Optional[AuthenticatedSession] = None
):
    auth = egs.get_authenticated_session(authenticated_session)
    req = DeleteGprRequest(gpr_id=request_id)
    api_response = auth.client.invoke_sdk_operation("/api/v1/gpr", "DELETE", req)
    if api_response.status_code != 200:
        raise GpuAlreadyProvisioned(api_response)
    return


def update_gpu_request_priority(
    request_id: str,
    new_priority: int,
    authenticated_session: Optional[AuthenticatedSession] = None,
):
    auth = egs.get_authenticated_session(authenticated_session)
    req = UpdateGprPriorityRequest(gpr_id=request_id, priority=new_priority)
    api_response = auth.client.invoke_sdk_operation("/api/v1/gpr", "PUT", req)
    if api_response.status_code != 200:
        raise GpuAlreadyProvisioned(api_response)
    return


def update_gpu_request_name(
    request_id: str,
    new_name: str,
    authenticated_session: Optional[AuthenticatedSession] = None,
):
    auth = egs.get_authenticated_session(authenticated_session)
    req = UpdateGprNameRequest(gpr_id=request_id, gpr_name=new_name)
    api_response = auth.client.invoke_sdk_operation("/api/v1/gpr", "PUT", req)
    if api_response.status_code != 200:
        raise GpuAlreadyProvisioned(api_response)
    return


def release_gpu(
    request_id: str, authenticated_session: Optional[AuthenticatedSession] = None
):
    auth = egs.get_authenticated_session(authenticated_session)
    req = GprReleaseRequest(gpr_id=request_id)
    api_response = auth.client.invoke_sdk_operation("/api/v1/gpr", "PUT", req)
    if api_response.status_code != 200:
        raise GpuAlreadyReleased(api_response)
    return


def gpu_request_status(
    request_id: str, authenticated_session: Optional[AuthenticatedSession] = None
) -> GpuRequestData:
    auth = egs.get_authenticated_session(authenticated_session)
    api_response = auth.client.invoke_sdk_operation(
        "/api/v1/gpr?gprId=" + request_id, "GET"
    )
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return GpuRequestData(**api_response.data)


def gpu_request_status_for_workspace(
    workspace_name: str, authenticated_session: Optional[AuthenticatedSession] = None
):
    auth = egs.get_authenticated_session(authenticated_session)
    api_response = auth.client.invoke_sdk_operation(
        "/api/v1/gpr/list?sliceName=" + workspace_name, "GET"
    )
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return WorkspaceGpuRequestDataResponse(**api_response.data)
