from typing import List, Optional

import egs
from egs.authenticated_session import AuthenticatedSession
from egs.exceptions import UnhandledException
from egs.internal.inference_endpoint.create_inference_endpoint_data import (
    Autoscaling,
    CreateInferenceEndpointRequest,
    CreateInferenceEndpointResponse,
    GpuSpec,
    ModelSpec,
)
from egs.internal.inference_endpoint.delete_inference_endpoint_data import (
    DeleteInferenceEndpointRequest,
    DeleteInferenceEndpointResponse,
)
from egs.internal.inference_endpoint.describe_inference_endpoint_data import (
    DescribeInferenceEndpointResponse,
)
from egs.internal.inference_endpoint.list_inference_endpoint_data import (
    ListInferenceEndpointResponse,
)


def list_inference_endpoints(
    workspace_name: str, authenticated_session: AuthenticatedSession | None = None
) -> ListInferenceEndpointResponse:
    auth = egs.get_authenticated_session(authenticated_session)
    api_response = auth.client.invoke_sdk_operation(
        "/api/v1/inference-endpoint/list?workspace=" + workspace_name, "GET"
    )
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return ListInferenceEndpointResponse(**api_response.data)


def create_inference_endpoint(
    endpoint_name: str,
    workspace_name: str,
    standard_model_spec: ModelSpec,
    gpu_spec: GpuSpec,
    cluster_precedence: List[str] = [],
    cluster_name: str = "",
    burst: bool = False,
    autoscaling: Optional[Autoscaling] = None,
    authenticated_session: Optional[AuthenticatedSession] = None,
) -> CreateInferenceEndpointResponse:
    auth = egs.get_authenticated_session(authenticated_session)
    req = CreateInferenceEndpointRequest(
        cluster_name=cluster_name,
        cluster_precedence=cluster_precedence,
        autoscaling=autoscaling,
        burst=burst,
        endpoint_name=endpoint_name,
        workspace=workspace_name,
        model_spec=standard_model_spec,
        gpu_spec=gpu_spec,
        raw_model_spec=None,
    )
    api_response = auth.client.invoke_sdk_operation(
        "/api/v1/inference-endpoint", "POST", req
    )
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return CreateInferenceEndpointResponse(**api_response.data)


def create_inference_endpoint_with_custom_model_spec(
    endpoint_name: str,
    workspace_name: str,
    raw_model_spec: str,
    gpu_spec: GpuSpec,
    cluster_name: str = "",
    cluster_precedence: List[str] = [],
    autoscaling: Optional[Autoscaling] = None,
    authenticated_session: Optional[AuthenticatedSession] = None,
) -> CreateInferenceEndpointResponse:
    auth = egs.get_authenticated_session(authenticated_session)
    req = CreateInferenceEndpointRequest(
        cluster_name=cluster_name,
        cluster_precedence=cluster_precedence,
        endpoint_name=endpoint_name,
        workspace=workspace_name,
        autoscaling=autoscaling,
        gpu_spec=gpu_spec,
        raw_model_spec=raw_model_spec,
        model_spec=None,
    )
    api_response = auth.client.invoke_sdk_operation(
        "/api/v1/inference-endpoint", "POST", req
    )
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return CreateInferenceEndpointResponse(**api_response.data)


def describe_inference_endpoint(
    workspace_name: str,
    endpoint_name: str,
    cluster_name: str,
    authenticated_session: Optional[AuthenticatedSession] = None,
) -> DescribeInferenceEndpointResponse:
    auth = egs.get_authenticated_session(authenticated_session)
    api_response = auth.client.invoke_sdk_operation(
        f"/api/v1/inference-endpoint?workspace={workspace_name}&endpoint={endpoint_name}&cluster={cluster_name}",
        "GET",
    )
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return DescribeInferenceEndpointResponse(**api_response.data)


def delete_inference_endpoint(
    workspace_name: str,
    endpoint_name: str,
    cluster_name: str,
    authenticated_session: Optional[AuthenticatedSession] = None,
) -> DeleteInferenceEndpointResponse:
    auth = egs.get_authenticated_session(authenticated_session)
    req = DeleteInferenceEndpointRequest(
        workspace_name=workspace_name,
        endpoint_name=endpoint_name,
        cluster_name=cluster_name,
    )
    api_response = auth.client.invoke_sdk_operation(
        "/api/v1/inference-endpoint", "DELETE", req
    )
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return DeleteInferenceEndpointResponse(**api_response.data)
