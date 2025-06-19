import egs
from egs.authenticated_session import AuthenticatedSession
from egs.exceptions import WorkspaceAlreadyExists, BadParameters, UnhandledException, Unauthorized
from egs.internal.workspace.create_workspace_data import CreateWorkspaceRequest, CreateWorkspaceResponse
from egs.internal.workspace.delete_workspace_data import DeleteWorkspaceRequest, DeleteWorkspaceResponse
from egs.internal.workspace.update_workspace_data import UpdateWorkspaceRequest, UpdateWorkspaceResponse, DetachClusterRequest, DetachClusterResponse
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
    auth = egs.get_authenticated_session(authenticated_session)
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

def update_workspace(
        workspace_name: str,
        clusters: [str] = None,
        namespaces: [str] = None,
        authenticated_session: AuthenticatedSession = None
) -> str:
    """
    Updates an existing workspace with new clusters and/or namespaces.
    If clusters or namespaces is None, the existing values will be preserved.
    """
    auth = egs.get_authenticated_session(authenticated_session)
    
    # If either clusters or namespaces is None, we need to get current workspace details
    if clusters is None or namespaces is None:
        current_workspace = _get_workspace_details(workspace_name, auth)
        if clusters is None:
            clusters = current_workspace.clusters
        if namespaces is None:
            # Extract namespace names from the Namespace objects
            namespaces = [ns.namespace for ns in current_workspace.namespaces]
    
    req = UpdateWorkspaceRequest(
        workspace_name=workspace_name,
        clusters=clusters,
        namespaces=namespaces
    )
    api_response = auth.client.invoke_sdk_operation('/api/v1/slice-workspace', 'PUT', req)
    if api_response.status_code == 404:
        raise ValueError(f"Workspace '{workspace_name}' not found")
    elif api_response.status_code == 422:
        raise BadParameters(api_response)
    elif api_response.status_code != 200:
        raise UnhandledException(api_response)
    return UpdateWorkspaceResponse(**api_response.data).workspace_name

def detach_cluster_from_workspace(
        workspace_name: str,
        cluster_name: str,
        authenticated_session: AuthenticatedSession = None
) -> str:
    """
    Detaches a cluster from a workspace/slice.
    
    Args:
        workspace_name (str): Name of the workspace/slice
        cluster_name (str): Name of the cluster to detach
        authenticated_session: Optional authenticated session
        
    Returns:
        str: Name of the workspace after detaching the cluster
        
    Raises:
        ValueError: If workspace not found or cluster not in workspace
        UnhandledException: If API call fails
    """
    auth = egs.get_authenticated_session(authenticated_session)
    
    # Get current workspace details
    current_workspace = _get_workspace_details(workspace_name, auth)
    
    # Check if cluster exists in the workspace
    if cluster_name not in current_workspace.clusters:
        raise ValueError(f"Cluster '{cluster_name}' is not attached to workspace '{workspace_name}'")
    
    # Remove the cluster from the list
    updated_clusters = [c for c in current_workspace.clusters if c != cluster_name]
    
    if len(updated_clusters) == 0:
        raise ValueError(f"Cannot detach the last cluster from workspace '{workspace_name}'. At least one cluster must remain.")
    
    # Extract namespace names from the Namespace objects
    current_namespaces = [ns.namespace for ns in current_workspace.namespaces]
    
    # Update the workspace with the new cluster list
    return update_workspace(
        workspace_name=workspace_name,
        clusters=updated_clusters,
        namespaces=current_namespaces,
        authenticated_session=auth
    )

def _get_workspace_details(workspace_name: str, auth: AuthenticatedSession) -> Workspace:
    """
    Helper function to get details of a specific workspace.
    
    Args:
        workspace_name (str): Name of the workspace to find
        auth: Authenticated session
        
    Returns:
        Workspace: The workspace object
        
    Raises:
        ValueError: If workspace not found
    """
    workspaces_response = list_workspaces(auth)
    for workspace in workspaces_response.workspaces:
        if workspace.name == workspace_name:
            return workspace
    raise ValueError(f"Workspace '{workspace_name}' not found")

def delete_workspace(
        workspace_name: str,
        authenticated_session: AuthenticatedSession = None
):
    auth = egs.get_authenticated_session(authenticated_session)
    req = DeleteWorkspaceRequest(
        workspace_name=workspace_name
    )
    api_response = auth.client.invoke_sdk_operation('/api/v1/slice-workspace', 'DELETE', req)
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return DeleteWorkspaceResponse(**api_response.data)

def list_workspaces(
        authenticated_session: AuthenticatedSession = None
) -> ListWorkspacesResponse:
    auth = egs.get_authenticated_session(authenticated_session)
    api_response = auth.client.invoke_sdk_operation('/api/v1/slice-workspace/list', 'GET')
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return ListWorkspacesResponse(**api_response.data)

def get_workspace_kubeconfig(
        workspace_name: str,
        cluster_name: str,
        authenticated_session: AuthenticatedSession = None
):
    auth = egs.get_authenticated_session(authenticated_session)
    req = GenerateWorkspaceKubeConfigRequest(
        workspace_name=workspace_name,
        cluster_name=cluster_name
    )
    api_response = auth.client.invoke_sdk_operation('/api/v1/slice-workspace/kube-config', 'POST', req)
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return GenerateWorkspaceKubeConfigResponse(**api_response.data).kube_config
