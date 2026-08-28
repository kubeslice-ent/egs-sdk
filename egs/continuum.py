import urllib.parse

import egs
from egs.authenticated_session import AuthenticatedSession
from egs.exceptions import UnhandledException
from egs.internal.continuum.continuum_data import (
    CapacityLandscape,
    ContinuumGroup,
    ContinuumGroupDetail,
    ContinuumMetrics,
    CreateContinuumGroupRequest,
    DeleteContinuumGroupResponse,
    ListContinuumGroupsResponse,
    UpdateContinuumGroupBody,
)


def list_continuum_groups(
        authenticated_session: AuthenticatedSession = None
) -> ListContinuumGroupsResponse:
    """List all continuum groups (edge->core tiers) configured in the platform."""
    auth = egs.get_authenticated_session(authenticated_session)
    api_response = auth.client.invoke_sdk_operation(
        '/api/v1/continuum-group/list', 'GET'
    )
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return ListContinuumGroupsResponse(**api_response.data)


def create_continuum_group(
        name: str,
        label: str,
        icon: str,
        authenticated_session: AuthenticatedSession = None
) -> ContinuumGroup:
    """Create a new continuum group."""
    auth = egs.get_authenticated_session(authenticated_session)
    req = CreateContinuumGroupRequest(name=name, label=label, icon=icon)
    api_response = auth.client.invoke_sdk_operation(
        '/api/v1/continuum-group/create', 'POST', req
    )
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return ContinuumGroup(**api_response.data)


def update_continuum_group(
        name: str,
        label: str,
        icon: str,
        authenticated_session: AuthenticatedSession = None
) -> ContinuumGroup:
    """Update the label and icon of an existing continuum group."""
    auth = egs.get_authenticated_session(authenticated_session)
    req = UpdateContinuumGroupBody(label=label, icon=icon)
    resource = '/api/v1/continuum-group?name=' + urllib.parse.quote(name, safe='')
    api_response = auth.client.invoke_sdk_operation(resource, 'PUT', req)
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return ContinuumGroup(**api_response.data)


def delete_continuum_group(
        name: str,
        authenticated_session: AuthenticatedSession = None
) -> DeleteContinuumGroupResponse:
    """Delete a continuum group by name."""
    auth = egs.get_authenticated_session(authenticated_session)
    resource = '/api/v1/continuum-group?name=' + urllib.parse.quote(name, safe='')
    api_response = auth.client.invoke_sdk_operation(resource, 'DELETE')
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return DeleteContinuumGroupResponse(**api_response.data)


def get_continuum_metrics(
        authenticated_session: AuthenticatedSession = None
) -> ContinuumMetrics:
    """Fetch the aggregate continuum map metrics (overall metrics, tier cards,
    and the workspace/tier placement matrix) rendered by the dashboard."""
    auth = egs.get_authenticated_session(authenticated_session)
    api_response = auth.client.invoke_sdk_operation(
        '/api/v1/continuum-group/metrics', 'GET'
    )
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return ContinuumMetrics(**api_response.data)


def get_continuum_group_detail(
        name: str,
        authenticated_session: AuthenticatedSession = None
) -> ContinuumGroupDetail:
    """Fetch the detail view for a single continuum group: tier summary,
    member clusters, and active workloads."""
    auth = egs.get_authenticated_session(authenticated_session)
    resource = (
        '/api/v1/continuum-group/detail?name=' + urllib.parse.quote(name, safe='')
    )
    api_response = auth.client.invoke_sdk_operation(resource, 'GET')
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return ContinuumGroupDetail(**api_response.data)


def get_capacity_landscape(
        workspace: str,
        authenticated_session: AuthenticatedSession = None
) -> CapacityLandscape:
    """Fetch the capacity landscape for a given workspace."""
    auth = egs.get_authenticated_session(authenticated_session)
    resource = (
        '/api/v1/continuum-group/capacity-landscape?workspace='
        + urllib.parse.quote(workspace, safe='')
    )
    api_response = auth.client.invoke_sdk_operation(resource, 'GET')
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return CapacityLandscape(**api_response.data)
