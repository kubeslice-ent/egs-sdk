from typing import Optional, List, Dict

import egs
from egs.authenticated_session import AuthenticatedSession
from egs.exceptions import UnhandledException

from egs.internal.gpr_template_binding.create_gpr_template_binding import (
    GprTemplateBindingCluster,
    CreateGprTemplateBindingRequest,
    CreateGprTemplateBindingResponse,
)
from egs.internal.gpr_template_binding.get_gpr_template_binding import (
    GetGprTemplateBindingResponse,
)
from egs.internal.gpr_template_binding.list_gpr_template_binding import (
    ListGprTemplateBindingsRequest,
    ListGprTemplateBindingsResponse,
)
from egs.internal.gpr_template_binding.delete_gpr_template_binding import (
    DeleteGprTemplateBindingRequest,
    DeleteGprTemplateBindingResponse,
)
from egs.internal.gpr_template_binding.update_gpr_template_binding import (
    UpdateGprTemplateBindingRequest,
    UpdateGprTemplateBindingResponse,
)


def create_gpr_template_binding(
    workspace_name: str,
    clusters: List[Dict],
    enable_auto_gpr: bool,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> CreateGprTemplateBindingResponse:
    """
    Creates a GPR template binding.

    Args:
        workspace_name (str): Workspace name (slice name).
        clusters (List[Dict]): List of cluster dicts.
        enable_auto_gpr (bool): Enable auto GPR flag.
        authenticated_session (Optional[AuthenticatedSession]): Session.

    Returns:
        CreateGprTemplateBindingResponse
    """
    auth = egs.get_authenticated_session(authenticated_session)

    cluster_objs = [
        GprTemplateBindingCluster(
            cluster_name=cluster.get("clusterName"),
            default_template_name=cluster.get("defaultTemplateName"),
            templates=cluster.get("templates", [])
        ) for cluster in clusters
    ]

    request_payload = CreateGprTemplateBindingRequest(
        workspace_name=workspace_name,
        clusters=cluster_objs,
        enable_auto_gpr=enable_auto_gpr
    )

    response = auth.client.invoke_sdk_operation(
        "/api/v1/gpr-template-binding", "POST", request_payload
    )

    if response.status_code != 200:
        raise UnhandledException(response)

    return CreateGprTemplateBindingResponse(**response.data)


def get_gpr_template_binding(
    binding_name: str,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> GetGprTemplateBindingResponse:
    """
    Gets a GPR template binding by name.

    Args:
        binding_name (str): GPR template binding name.
        authenticated_session (Optional[AuthenticatedSession]): Session.

    Returns:
        GetGprTemplateBindingResponse
    """
    auth = egs.get_authenticated_session(authenticated_session)

    endpoint = (
        f"/api/v1/gpr-template-binding?gprTemplateBindingName={binding_name}"
    )
    response = auth.client.invoke_sdk_operation(endpoint, "GET")

    if response.status_code != 200:
        raise UnhandledException(response)

    return GetGprTemplateBindingResponse(**response.data)


def list_gpr_template_bindings(
    authenticated_session: Optional[AuthenticatedSession] = None
) -> ListGprTemplateBindingsResponse:
    """
    Lists all GPR template bindings.

    Args:
        authenticated_session (Optional[AuthenticatedSession]): Session.

    Returns:
        ListGprTemplateBindingsResponse
    """
    auth = egs.get_authenticated_session(authenticated_session)

    response = auth.client.invoke_sdk_operation(
        "/api/v1/gpr-template-binding/list",
        "GET",
        ListGprTemplateBindingsRequest()
    )

    if response.status_code != 200:
        raise UnhandledException(response)

    return ListGprTemplateBindingsResponse(
        templateBindings=response.data.get("templateBindings", [])
    )


def update_gpr_template_binding(
    workspace_name: str,
    clusters: List[Dict],
    enable_auto_gpr: bool,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> UpdateGprTemplateBindingResponse:
    """
    Updates a GPR template binding.

    Args:
        workspace_name (str): The workspace/slice name.
        clusters (List[Dict]): List of cluster dicts.
        enable_auto_gpr (bool): Enable auto GPR flag.
        authenticated_session (Optional[AuthenticatedSession]): Session.

    Returns:
        UpdateGprTemplateBindingResponse
    """
    auth = egs.get_authenticated_session(authenticated_session)

    cluster_objs = [
        GprTemplateBindingCluster(
            cluster_name=cluster.get("clusterName"),
            default_template_name=cluster.get("defaultTemplateName"),
            templates=cluster.get("templates", [])
        ) for cluster in clusters
    ]

    request_payload = UpdateGprTemplateBindingRequest(
        workspace_name=workspace_name,
        clusters=cluster_objs,
        enable_auto_gpr=enable_auto_gpr
    )

    response = auth.client.invoke_sdk_operation(
        "/api/v1/gpr-template-binding", "PUT", request_payload
    )

    if response.status_code != 200:
        raise UnhandledException(response)

    return UpdateGprTemplateBindingResponse(**response.data)


def delete_gpr_template_binding(
    binding_name: str,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> DeleteGprTemplateBindingResponse:
    """
    Deletes a GPR template binding by name.

    Args:
        binding_name (str): Name of the binding to delete.
        authenticated_session (Optional[AuthenticatedSession]): Session.

    Returns:
        DeleteGprTemplateBindingResponse
    """
    auth = egs.get_authenticated_session(authenticated_session)

    request_payload = DeleteGprTemplateBindingRequest(
        gpr_template_binding_name=binding_name
    )

    response = auth.client.invoke_sdk_operation(
        "/api/v1/gpr-template-binding", "DELETE", request_payload
    )

    if response.status_code != 200:
        raise UnhandledException(response)

    return DeleteGprTemplateBindingResponse()
