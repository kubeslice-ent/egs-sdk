# tests/test_workspace.py
import pytest
import egs
from egs.internal.workspace.list_workspaces_data import ListWorkspacesResponse


def test_list_workspaces(auth_session, workspace):
    ws_name, clusters, namespaces, username, email = workspace
    resp = egs.list_workspaces(authenticated_session=auth_session)
    assert isinstance(resp, ListWorkspacesResponse)
    names = [w.name for w in resp.workspaces]
    assert ws_name in names


def test_get_workspace_kubeconfig(auth_session, workspace):
    ws_name, clusters, namespaces, username, email = workspace
    cluster = clusters[0]
    # Retry fetching kubeconfig until it becomes available
    import time
    from egs.exceptions import UnhandledException

    kubeconfig = None
    for _ in range(6):  # up to ~30 seconds
        try:
            kubeconfig = egs.get_workspace_kubeconfig(
                workspace_name=ws_name,
                cluster_name=cluster,
                authenticated_session=auth_session
            )
            break
        except UnhandledException as e:
            # Wait if not yet ready
            if 'No record found for slice' in str(e):
                time.sleep(5)
                continue
            else:
                raise
    assert isinstance(kubeconfig, str), "Failed to retrieve kubeconfig for workspace"
    assert kubeconfig.startswith("apiVersion") 