import egs
from egs.authenticated_session import AuthenticatedSession
from egs.exceptions import WorkspaceAlreadyExists, BadParameters, UnhandledException
from egs.internal.workspace.create_workspace_data import CreateWorkspaceRequest, CreateWorkspaceResponse
from egs.internal.workspace.delete_workspace_data import DeleteWorkspaceRequest, DeleteWorkspaceResponse
from egs.internal.workspace.list_workspaces_data import ListWorkspacesResponse, Workspace
from egs.internal.workspace.workspace_kube_config_data import GenerateWorkspaceKubeConfigRequest, \
    GenerateWorkspaceKubeConfigResponse


def create_workspace(
        workspace_name: str,
        clusters: [str],
        namespaces: [str],
        username: str,
        email: str,
        authenticated_session: AuthenticatedSession = None
) -> str:
    auth = egs.get_global_session()
    if authenticated_session is not None:
        auth = authenticated_session
    req = CreateWorkspaceRequest(
        workspace_name=workspace_name,
        clusters=clusters,
        namespaces=namespaces,
        username=username,
        email=email
    )
    api_response = auth.client.invoke_sdk_operation('/api/v1/slice-workspace', 'POST', req)
    if api_response.status_code == 409:
        raise WorkspaceAlreadyExists(api_response)
    elif api_response.status_code == 422:
        raise BadParameters(api_response)
    elif api_response.status_code != 200:
        raise UnhandledException(api_response)
    return CreateWorkspaceResponse(**api_response.data).workspace_name

def delete_workspace(
        workspace_name: str,
        authenticated_session: AuthenticatedSession = None
):
    auth = egs.get_global_session()
    if authenticated_session is not None:
        auth = authenticated_session
    req = DeleteWorkspaceRequest(
        workspace_name=workspace_name
    )
    api_response = auth.client.invoke_sdk_operation('/api/v1/slice-workspace', 'DELETE', req)
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return DeleteWorkspaceResponse(**api_response.data)

def list_workspaces(
        authenticated_session: AuthenticatedSession = None
) -> [Workspace]:
    auth = egs.get_global_session()
    if authenticated_session is not None:
        auth = authenticated_session
    api_response = auth.client.invoke_sdk_operation('/api/v1/slice-workspace/list', 'GET')
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    workspaces = ListWorkspacesResponse(**api_response.data).workspaces
    w = []
    for i in workspaces:
        w.append(Workspace(**i))
    return w

def get_workspace_kubeconfig(
        workspace_name: str,
        authenticated_session: AuthenticatedSession = None
):
    auth = egs.get_global_session()
    if authenticated_session is not None:
        auth = authenticated_session
    req = GenerateWorkspaceKubeConfigRequest(
        workspace_name=workspace_name
    )
    api_response = auth.client.invoke_sdk_operation('/api/v1/slice-workspace/kube-config', 'POST', req)
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return GenerateWorkspaceKubeConfigResponse(**api_response.data).kube_config
