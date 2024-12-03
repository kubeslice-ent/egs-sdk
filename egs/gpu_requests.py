from egs.authenticated_session import AuthenticatedSession
from egs.exceptions import UnhandledException, GpuAlreadyProvisioned, GpuAlreadyReleased
from egs.internal.gpr.create_gpr_data import CreateGprRequest, CreateGprResponse
from egs.internal.gpr.delete_gpr_data import DeleteGprRequest, DeleteGprResponse
from egs.internal.gpr.gpr_release_data import GprReleaseRequest
from egs.internal.gpr.gpr_status_data import GpuRequestData, WorkspaceGpuRequestDataResponse
from egs.internal.gpr.update_gpr_name_data import UpdateGprNameRequest
from egs.internal.gpr.update_gpr_priority_data import UpdateGprPriorityRequest


def request_gpu(
        request_name: str,
        workspace_name: str,
        cluster_name: str,
        node_count: int,
        gpu_per_node_count: int,
        memory_per_gpu: int,
        instance_type: str,
        gpu_name: str,
        exit_duration: str,
        priority: int,
        authenticated_session: AuthenticatedSession = None
) -> str:
    # auth = _authenticated_session
    # if authenticated_session is not None:
    auth = authenticated_session
    req = CreateGprRequest(
        request_name=request_name,
        workspace_name=workspace_name,
        cluster_name=cluster_name,
        node_count=node_count,
        gpu_per_node_count=gpu_per_node_count,
        memory_per_gpu=memory_per_gpu,
        instance_type=instance_type,
        gpu_name=gpu_name,
        exit_duration=exit_duration,
        priority=priority
    )
    api_response = auth.client.invoke_sdk_operation('/api/v1/gpr', 'POST', req)
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return CreateGprResponse(**api_response.data).gpr_id


def cancel_gpu_request(
        request_id: str,
        authenticated_session: AuthenticatedSession = None
):
    # auth = _authenticated_session
    # if authenticated_session is not None:
    auth = authenticated_session
    req = DeleteGprRequest(
        gpr_id=request_id
    )
    api_response = auth.client.invoke_sdk_operation('/api/v1/gpr', 'DELETE', req)
    if api_response.status_code != 200:
        raise GpuAlreadyProvisioned(api_response)
    return

def update_gpu_request_priority(
        request_id: str,
        new_priority: int,
        authenticated_session: AuthenticatedSession = None
):
    # auth = _authenticated_session
    # if authenticated_session is not None:
    auth = authenticated_session
    req = UpdateGprPriorityRequest(
        gpr_id=request_id,
        priority=new_priority
    )
    api_response = auth.client.invoke_sdk_operation('/api/v1/gpr', 'PUT', req)
    if api_response.status_code != 200:
        raise GpuAlreadyProvisioned(api_response)
    return


def update_gpu_request_name(
        request_id: str,
        new_name: str,
        authenticated_session: AuthenticatedSession = None
):
    # auth = _authenticated_session
    # if authenticated_session is not None:
    auth = authenticated_session
    req = UpdateGprNameRequest(
        gpr_id=request_id,
        gpr_name=new_name
    )
    api_response = auth.client.invoke_sdk_operation('/api/v1/gpr', 'PUT', req)
    if api_response.status_code != 200:
        raise GpuAlreadyProvisioned(api_response)
    return


def release_gpu(
        request_id: str,
        authenticated_session: AuthenticatedSession = None
):
    # auth = _authenticated_session
    # if authenticated_session is not None:
    auth = authenticated_session
    req = GprReleaseRequest(
        gpr_id=request_id
    )
    api_response = auth.client.invoke_sdk_operation('/api/v1/gpr', 'PUT', req)
    if api_response.status_code != 200:
        raise GpuAlreadyReleased(api_response)
    return


def gpu_request_status(
        request_id: str,
        authenticated_session: AuthenticatedSession = None
) -> GpuRequestData:
    # auth = _authenticated_session
    # if authenticated_session is not None:
    auth = authenticated_session
    api_response = auth.client.invoke_sdk_operation('/api/v1/gpr?gprId=' + request_id, 'GET')
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return GpuRequestData(**api_response.data)


def gpu_request_status_for_workspace(
        workspace_name: str,
        authenticated_session: AuthenticatedSession = None
):
    # auth = _authenticated_session
    # if authenticated_session is not None:
    auth = authenticated_session
    api_response = auth.client.invoke_sdk_operation('/api/v1/gpr/list?sliceName=' + workspace_name, 'GET')
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return WorkspaceGpuRequestDataResponse(**api_response.data)