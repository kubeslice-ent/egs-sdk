from typing import Optional
import egs
from egs.authenticated_session import AuthenticatedSession
from egs.exceptions import UnhandledException
from egs.internal.gpr_template.create_gpr_template import (
    CreateGprTemplateRequest, CreateGprTemplateResponse)
from egs.internal.gpr_template.get_gpr_template import (
     GetGprTemplateResponse)
from egs.internal.gpr_template.list_gpr_templates import (
    ListGprTemplatesRequest, ListGprTemplatesResponse)
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
    Creates a GPR template using the provided parameters and returns the
    template name.
    """
    if enforce_idle_timeout and not idle_timeout_duration:
        raise ValueError("idle_timeout_duration is required when enforce_idle_timeout is True")

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
        idle_timeout_duration=idle_timeout_duration
    )

    api_response = auth.client.invoke_sdk_operation(
        '/api/v1/gpr-template',
        'POST',
        request_payload
    )

    if api_response.status_code != 200:
        raise UnhandledException(api_response)

    return CreateGprTemplateResponse(**api_response.data).gpr_template_name


def get_gpr_template(
    gpr_template_name: str,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> GetGprTemplateResponse:
    """
    Retrieves a GPR template by its name.
    
    :param gpr_template_name: Name of the GPR template.
    :param authenticated_session: Optional authenticated session.
    :return: GetGprTemplateResponse object.
    """
    auth = egs.get_authenticated_session(authenticated_session)

    api_response = auth.client.invoke_sdk_operation(
        '/api/v1/gpr-template?gprTemplateName=' + gpr_template_name,
        'GET')

    if api_response.status_code != 200:
        raise UnhandledException(api_response)

    return GetGprTemplateResponse(**api_response.data)


def list_gpr_templates(
    authenticated_session: Optional[AuthenticatedSession] = None
) -> ListGprTemplatesResponse:
    """
    Retrieves a list of all GPR templates.
    
    :param authenticated_session: Optional authenticated session.
    :return: ListGprTemplatesResponse object.
    """
    auth = egs.get_authenticated_session(authenticated_session)

    request_payload = ListGprTemplatesRequest()

    api_response = auth.client.invoke_sdk_operation(
        '/api/v1/gpr-template/list',
        'GET',
        request_payload
    )

    if api_response.status_code != 200:
        raise UnhandledException(api_response)

    return ListGprTemplatesResponse(items=api_response.data.get("items", []))


def update_gpr_template(
    name: str,
    cluster_name: str,
    number_of_gpus: int,
    instance_type: str,
    exit_duration: str,
    number_of_gpu_nodes: int,
    priority: int,
    gpu_sharing_mode: str,
    memory_per_gpu: int,
    gpu_shape: str,
    enable_eviction: bool,
    requeue_on_failure: bool,
    idle_timeout_duration: str,
    enforce_idle_timeout: bool,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> UpdateGprTemplateResponse:
    """
    Update an existing GPR Template.
    """
    auth = egs.get_authenticated_session(authenticated_session)

    req = UpdateGprTemplateRequest(
        name=name,
        cluster_name=cluster_name,
        number_of_gpus=number_of_gpus,
        instance_type=instance_type,
        exit_duration=exit_duration,
        number_of_gpu_nodes=number_of_gpu_nodes,
        priority=priority,
        gpu_sharing_mode=gpu_sharing_mode,
        memory_per_gpu=memory_per_gpu,
        gpu_shape=gpu_shape,
        enable_eviction=enable_eviction,
        requeue_on_failure=requeue_on_failure,
        idle_timeout_duration=idle_timeout_duration,
        enforce_idle_timeout=enforce_idle_timeout,
    )

    api_response = auth.client.invoke_sdk_operation(
        "/api/v1/gpr-template", "PUT", req
    )

    if api_response.status_code != 200:
        raise UnhandledException(api_response)

    return UpdateGprTemplateResponse()


def delete_gpr_template(
    gpr_template_name: str,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> DeleteGprTemplateResponse:
    """
    Delete a GPR Template by name.
    """
    auth = egs.get_authenticated_session(authenticated_session)

    req = DeleteGprTemplateRequest(gpr_template_name)

    api_response = auth.client.invoke_sdk_operation(
        "/api/v1/gpr-template", "DELETE", req
    )

    if api_response.status_code != 200:
        raise UnhandledException(api_response)

    return DeleteGprTemplateResponse()
