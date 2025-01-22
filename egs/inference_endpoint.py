import egs
from egs.authenticated_session import AuthenticatedSession
from egs.exceptions import UnhandledException
from egs.internal.inference_endpoint.create_inference_endpoint_data import CreateInferenceEndpointResponse, ModelSpec, \
    GpuSpec, CreateInferenceEndpointRequest
from egs.internal.inference_endpoint.delete_inference_endpoint_data import DeleteInferenceEndpointResponse, \
    DeleteInferenceEndpointRequest
from egs.internal.inference_endpoint.describe_inference_endpoint_data import DescribeInferenceEndpointResponse
from egs.internal.inference_endpoint.list_inference_endpoint_data import ListInferenceEndpointResponse

def list_inference_endpoints(
        workspace_name: str,
        authenticated_session: AuthenticatedSession = None
) -> ListInferenceEndpointResponse:
    auth = egs.get_authenticated_session(authenticated_session)
    api_response = auth.client.invoke_sdk_operation('/api/v1/inference-endpoint/list?workspace=' + workspace_name, 'GET')
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return ListInferenceEndpointResponse(**api_response.data)

def create_inference_endpoint(
        cluster_name: str,
        endpoint_name: str,
        workspace_name: str,
        standard_model_spec: ModelSpec,
        gpu_spec: GpuSpec,
        authenticated_session: AuthenticatedSession = None
) -> CreateInferenceEndpointResponse:
    auth = egs.get_authenticated_session(authenticated_session)
    req = CreateInferenceEndpointRequest(
        cluster_name=cluster_name,
        endpoint_name=endpoint_name,
        workspace=workspace_name,
        model_spec=standard_model_spec,
        gpu_spec=gpu_spec,
        raw_model_spec=None
    )
    api_response = auth.client.invoke_sdk_operation('/api/v1/inference-endpoint', 'POST', req)
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return CreateInferenceEndpointResponse(**api_response.data)

def create_inference_endpoint_with_custom_model_spec(
        cluster_name: str,
        endpoint_name: str,
        workspace_name: str,
        raw_model_spec: str,
        gpu_spec: GpuSpec | None,
        authenticated_session: AuthenticatedSession = None
) -> CreateInferenceEndpointResponse:
    auth = egs.get_authenticated_session(authenticated_session)
    req = CreateInferenceEndpointRequest(
        cluster_name=cluster_name,
        endpoint_name=endpoint_name,
        workspace=workspace_name,
        model_spec=None,
        gpu_spec=gpu_spec,
        raw_model_spec=raw_model_spec
    )
    api_response = auth.client.invoke_sdk_operation('/api/v1/inference-endpoint', 'POST', req)
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return CreateInferenceEndpointResponse(**api_response.data)

def describe_inference_endpoint(
        workspace_name: str,
        endpoint_name: str,
        cluster_name: str,
        authenticated_session: AuthenticatedSession = None
) -> DescribeInferenceEndpointResponse:
    auth = egs.get_authenticated_session(authenticated_session)
    api_response = auth.client.invoke_sdk_operation(f"/api/v1/inference-endpoint?workspace={workspace_name}&endpoint={endpoint_name}&cluster={cluster_name}", 'GET')
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return DescribeInferenceEndpointResponse(**api_response.data)

def delete_inference_endpoint(
        workspace_name: str,
        endpoint_name: str,
        cluster_name: str,
        authenticated_session: AuthenticatedSession = None
) -> DeleteInferenceEndpointResponse:
    auth = egs.get_authenticated_session(authenticated_session)
    req = DeleteInferenceEndpointRequest(
        workspace_name=workspace_name,
        endpoint_name=endpoint_name,
        cluster_name=cluster_name
    )
    api_response = auth.client.invoke_sdk_operation("/api/v1/inference-endpoint", 'DELETE', req)
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return DeleteInferenceEndpointResponse(**api_response.data)
