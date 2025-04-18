from typing import Optional

import egs
from egs.authenticated_session import AuthenticatedSession
from egs.exceptions import UnhandledException
from egs.internal.gpr_template.create_gpr_template import (
    CreateGprTemplateRequest,
    CreateGprTemplateResponse,
)
from egs.internal.gpr_template.get_gpr_template import (
    GetGprTemplateResponse,
)
from egs.internal.gpr_template.list_gpr_templates import (
    ListGprTemplatesRequest,
    ListGprTemplatesResponse,
)
from egs.internal.gpr_template.update_gpr_template import (
    UpdateGprTemplateRequest,
    UpdateGprTemplateResponse,
)
from egs.internal.gpr_template.delete_gpr_template import (
    DeleteGprTemplateRequest,
    DeleteGprTemplateResponse,
)


def create_gpr_template(
    name: str,
    cluster_name: str,
    gpu_per_node_count: int,
    num_gpu_nodes: int,
    memory_per_gpu: int,
    gpu_shape: str,
    instance_type: str,
    exit_duration: str,
    priority: int,
    enforce_idle_timeout: bool,
    enable_eviction: bool,
    requeue_on_failure: bool,
    idle_timeout_duration: Optional[str] = None,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> str:
    """
    Create a GPR template.

    Args:
        name (str): Template name.
        cluster_name (str): Name of the cluster.
        gpu_per_node_count (int): Number of GPUs per node.
        num_gpu_nodes (int): Number of GPU nodes.
        memory_per_gpu (int): Memory per GPU in GB.
        gpu_shape (str): Shape of the GPU (e.g., "A100").
        instance_type (str): Instance type (e.g., "a2-highgpu-2g").
        exit_duration (str): Exit duration in string format (e.g., "1h").
        priority (int): Priority value.
        enforce_idle_timeout (bool): Whether to enforce idle timeout.
        enable_eviction (bool): Whether eviction is enabled.
        requeue_on_failure (bool): Whether to requeue on failure.
        idle_timeout_duration (Optional[str]): Idle timeout duration if enforced.
        authenticated_session (Optional[AuthenticatedSession]): Auth session.

    Returns:
        str: Name of the created GPR template.

    Raises:
        ValueError: If idle timeout is enforced but duration is not provided.
        UnhandledException: If API call fails.
    """
    if enforce_idle_timeout and not idle_timeout_duration:
        raise ValueError(
            "idle_timeout_duration is required when "
            "enforce_idle_timeout is True"
        )

    auth = egs.get_authenticated_session(authenticated_session)
    request_payload = CreateGprTemplateRequest(
        name=name,
        cluster_name=cluster_name,
        gpu_per_node_count=gpu_per_node_count,
        num_gpu_nodes=num_gpu_nodes,
        memory_per_gpu=memory_per_gpu,
        gpu_shape=gpu_shape,
        instance_type=instance_type,
        exit_duration=exit_duration,
        priority=priority,
        enable_eviction=enable_eviction,
        requeue_on_failure=requeue_on_failure,
        enforce_idle_timeout=enforce_idle_timeout,
        idle_timeout_duration=idle_timeout_duration,
    )

    api_response = auth.client.invoke_sdk_operation(
        '/api/v1/gpr-template', 'POST', request_payload
    )

    if api_response.status_code != 200:
        raise UnhandledException(api_response)

    return CreateGprTemplateResponse(
        **api_response.data
    ).gpr_template_name


def get_gpr_template(
    gpr_template_name: str,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> GetGprTemplateResponse:
    """
    Retrieve a GPR template by name.

    Args:
        gpr_template_name (str): Name of the GPR template.
        authenticated_session (Optional[AuthenticatedSession]): Auth session.

    Returns:
        GetGprTemplateResponse: GPR template object.

    Raises:
        UnhandledException: If API call fails.
    """
    auth = egs.get_authenticated_session(authenticated_session)

    api_response = auth.client.invoke_sdk_operation(
        f'/api/v1/gpr-template?gprTemplateName={gpr_template_name}',
        'GET'
    )

    if api_response.status_code != 200:
        raise UnhandledException(api_response)

    return GetGprTemplateResponse(**api_response.data)


def list_gpr_templates(
    authenticated_session: Optional[AuthenticatedSession] = None
) -> ListGprTemplatesResponse:
    """
    List all GPR templates.

    Args:
        authenticated_session (Optional[AuthenticatedSession]): Auth session.

    Returns:
        ListGprTemplatesResponse: List of GPR templates.

    Raises:
        UnhandledException: If API call fails.
    """
    auth = egs.get_authenticated_session(authenticated_session)

    request_payload = ListGprTemplatesRequest()

    api_response = auth.client.invoke_sdk_operation(
        '/api/v1/gpr-template/list', 'GET', request_payload
    )

    if api_response.status_code != 200:
        raise UnhandledException(api_response)

    return ListGprTemplatesResponse(
        items=api_response.data.get("items", [])
    )


def update_gpr_template(
    name: str,
    cluster_name: str,
    number_of_gpus: int,
    instance_type: str,
    exit_duration: str,
    number_of_gpu_nodes: int,
    priority: int,
    memory_per_gpu: int,
    gpu_shape: str,
    enable_eviction: bool,
    requeue_on_failure: bool,
    enforce_idle_timeout: bool,
    idle_timeout_duration: Optional[str] = None,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> UpdateGprTemplateResponse:
    """
    Update an existing GPR template.

    Args:
        name (str): Name of the template.
        cluster_name (str): Cluster name.
        number_of_gpus (int): Total number of GPUs.
        instance_type (str): Instance type.
        exit_duration (str): Exit duration.
        number_of_gpu_nodes (int): Number of nodes.
        priority (int): Priority value.
        memory_per_gpu (int): Memory per GPU in GB.
        gpu_shape (str): GPU shape name.
        enable_eviction (bool): Enable eviction flag.
        requeue_on_failure (bool): Requeue on failure flag.
        enforce_idle_timeout (bool): Enforce idle timeout flag.
        idle_timeout_duration (Optional[str]): Timeout duration if enforced.
        authenticated_session (Optional[AuthenticatedSession]): Auth session.

    Returns:
        UpdateGprTemplateResponse

    Raises:
        UnhandledException: If API call fails.
    """
    auth = egs.get_authenticated_session(authenticated_session)

    request_payload = UpdateGprTemplateRequest(
        name=name,
        cluster_name=cluster_name,
        number_of_gpus=number_of_gpus,
        instance_type=instance_type,
        exit_duration=exit_duration,
        number_of_gpu_nodes=number_of_gpu_nodes,
        priority=priority,
        memory_per_gpu=memory_per_gpu,
        gpu_shape=gpu_shape,
        enable_eviction=enable_eviction,
        requeue_on_failure=requeue_on_failure,
        enforce_idle_timeout=enforce_idle_timeout,
        idle_timeout_duration=idle_timeout_duration,
    )

    api_response = auth.client.invoke_sdk_operation(
        '/api/v1/gpr-template', 'PUT', request_payload
    )

    if api_response.status_code != 200:
        raise UnhandledException(api_response)

    return UpdateGprTemplateResponse()


def delete_gpr_template(
    gpr_template_name: str,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> DeleteGprTemplateResponse:
    """
    Delete a GPR template.

    Args:
        gpr_template_name (str): Template name to delete.
        authenticated_session (Optional[AuthenticatedSession]): Auth session.

    Returns:
        DeleteGprTemplateResponse

    Raises:
        UnhandledException: If API call fails.
    """
    auth = egs.get_authenticated_session(authenticated_session)

    request_payload = DeleteGprTemplateRequest(gpr_template_name)

    api_response = auth.client.invoke_sdk_operation(
        '/api/v1/gpr-template', 'DELETE', request_payload
    )

    if api_response.status_code != 200:
        raise UnhandledException(api_response)

    return DeleteGprTemplateResponse()
