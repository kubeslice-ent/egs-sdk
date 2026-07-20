import pytest

from egs.exceptions import BadParameters, UnhandledException, WorkspaceAlreadyExists
from egs.workspace import (
    create_workspace,
    delete_workspace,
    get_workspace_kubeconfig,
    list_workspaces,
)
from tests.conftest import make_api_response


def test_create_workspace_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={"workspaceName": "ws-1"}
    )
    name = create_workspace(
        "ws-1",
        ["c1"],
        ["ns1"],
        "user",
        "user@example.com",
        authenticated_session=mock_session,
    )
    assert name == "ws-1"
    path, method, req = mock_session.client.invoke_sdk_operation.call_args[0]
    assert path == "/api/v1/slice-workspace"
    assert method == "POST"
    assert req.workspaceName == "ws-1"


def test_create_workspace_conflict(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=409
    )
    with pytest.raises(WorkspaceAlreadyExists):
        create_workspace(
            "ws-1",
            ["c1"],
            ["ns1"],
            "user",
            "user@example.com",
            authenticated_session=mock_session,
        )


def test_create_workspace_bad_params(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=422
    )
    with pytest.raises(BadParameters):
        create_workspace(
            "ws-1",
            ["c1"],
            ["ns1"],
            "user",
            "user@example.com",
            authenticated_session=mock_session,
        )


def test_create_workspace_unhandled(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=500
    )
    with pytest.raises(UnhandledException):
        create_workspace(
            "ws-1",
            ["c1"],
            ["ns1"],
            "user",
            "user@example.com",
            authenticated_session=mock_session,
        )


def test_delete_workspace_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(data={})
    result = delete_workspace("ws-1", authenticated_session=mock_session)
    assert result is not None
    path, method, req = mock_session.client.invoke_sdk_operation.call_args[0]
    assert method == "DELETE"
    assert req.workspaceName == "ws-1"


def test_delete_workspace_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=500
    )
    with pytest.raises(UnhandledException):
        delete_workspace("ws-1", authenticated_session=mock_session)


def test_list_workspaces_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={
            "workspaces": [
                {
                    "name": "ws-1",
                    "overlayNetworkDeploymentMode": "single",
                    "maxClusters": 2,
                    "sliceDescription": "desc",
                    "clusters": ["c1"],
                    "namespaces": [{"namespace": "ns1", "clusters": ["c1"]}],
                }
            ]
        }
    )
    result = list_workspaces(authenticated_session=mock_session)
    assert len(result.workspaces) == 1
    assert result.workspaces[0].name == "ws-1"


def test_list_workspaces_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=500
    )
    with pytest.raises(UnhandledException):
        list_workspaces(authenticated_session=mock_session)


def test_get_workspace_kubeconfig_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={"kubeConfig": "apiVersion: v1"}
    )
    result = get_workspace_kubeconfig(
        "ws-1", "c1", authenticated_session=mock_session
    )
    assert result == "apiVersion: v1"
    path, method, req = mock_session.client.invoke_sdk_operation.call_args[0]
    assert path == "/api/v1/slice-workspace/kube-config"
    assert method == "POST"
    assert req.workspaceName == "ws-1"
    assert req.clusterName == "c1"


def test_get_workspace_kubeconfig_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=404
    )
    with pytest.raises(UnhandledException):
        get_workspace_kubeconfig("ws-1", "c1", authenticated_session=mock_session)
