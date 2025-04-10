from typing import Optional

import egs
from egs.authenticated_session import AuthenticatedSession
from egs.exceptions import UnhandledException

from egs.internal.gpr_template_binding.create_gpr_template_binding import (
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
    request: CreateGprTemplateBindingRequest,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> CreateGprTemplateBindingResponse:
    """
    Create a GPR template binding.

    Args:
        request (CreateGprTemplateBindingRequest): The request object.
        authenticated_session (Optional[AuthenticatedSession]): Auth session.

    Returns:
        CreateGprTemplateBindingResponse
    """
    auth = egs.get_authenticated_session(authenticated_session)
    response = auth.client.invoke_sdk_operation(
        "/api/v1/gpr-template-binding",
        "POST",
        request
    )

    if response.status_code != 200:
        raise UnhandledException(response)

    return CreateGprTemplateBindingResponse(**response.data)


def delete_gpr_template_binding(
    gpr_template_binding_name: str,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> DeleteGprTemplateBindingResponse:
    """
    Delete a GPR template binding.

    Args:
        gpr_template_binding_name (str): Name of the binding to delete.
        authenticated_session (Optional[AuthenticatedSession]): Auth session.

    Returns:
        DeleteGprTemplateBindingResponse
    """
    auth = egs.get_authenticated_session(authenticated_session)
    req = DeleteGprTemplateBindingRequest(gpr_template_binding_name)

    response = auth.client.invoke_sdk_operation(
        "/api/v1/gpr-template-binding",
        "DELETE",
        req
    )

    if response.status_code != 200:
        raise UnhandledException(response)

    return DeleteGprTemplateBindingResponse()


def get_gpr_template_binding(
    gpr_template_binding_name: str,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> GetGprTemplateBindingResponse:
    """
    Retrieve a GPR template binding by name.

    Args:
        gpr_template_binding_name (str): Name of the binding.
        authenticated_session (Optional[AuthenticatedSession]): Auth session.

    Returns:
        GetGprTemplateBindingResponse
    """
    auth = egs.get_authenticated_session(authenticated_session)

    endpoint = f"/api/v1/gpr-template-binding?gprTemplateBindingName={gpr_template_binding_name}"
    response = auth.client.invoke_sdk_operation(endpoint, "GET")

    if response.status_code != 200:
        raise UnhandledException(response)

    return GetGprTemplateBindingResponse(**response.data)


def list_gpr_template_bindings(
    authenticated_session: Optional[AuthenticatedSession] = None
) -> ListGprTemplateBindingsResponse:
    """
    List all GPR template bindings.

    Args:
        authenticated_session (Optional[AuthenticatedSession]): Auth session.

    Returns:
        ListGprTemplateBindingsResponse
    """
    auth = egs.get_authenticated_session(authenticated_session)

    request = ListGprTemplateBindingsRequest()

    response = auth.client.invoke_sdk_operation(
        "/api/v1/gpr-template-binding/list",
        "GET",
        request
    )

    if response.status_code != 200:
        raise UnhandledException(response)

    return ListGprTemplateBindingsResponse(
        templateBindings=response.data.get("templateBindings", [])
    )


def update_gpr_template_binding(
    request: UpdateGprTemplateBindingRequest,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> UpdateGprTemplateBindingResponse:
    """
    Update an existing GPR template binding.

    Args:
        request (UpdateGprTemplateBindingRequest): The update payload.
        authenticated_session (Optional[AuthenticatedSession]): Auth session.

    Returns:
        UpdateGprTemplateBindingResponse

    Raises:
        UnhandledException: If API call fails.
    """
    auth = egs.get_authenticated_session(authenticated_session)

    response = auth.client.invoke_sdk_operation(
        "/api/v1/gpr-template-binding",
        "PUT",
        request
    )

    if response.status_code != 200:
        raise UnhandledException(response)

    return UpdateGprTemplateBindingResponse()
