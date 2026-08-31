import pytest

from egs.exceptions import UnhandledException
from egs.workload_placement import (
    create_workload_placement_from_manifest,
    delete_workload_placement,
    get_workload_placement,
    list_workload_placements,
    list_workload_placements_by_workspace,
)
from tests.conftest import make_api_response


SINGLE_MANIFEST = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: custom-server
spec:
  replicas: 1
"""

MULTI_MANIFEST = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: custom-server
spec:
  replicas: 1
---
apiVersion: v1
kind: Service
metadata:
  name: custom-server
spec:
  ports:
    - port: 80
"""


def test_create_workload_placement_from_single_manifest(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={"name": "custom-workload"}
    )

    result = create_workload_placement_from_manifest(
        workspace_name="ws-1",
        workload_name="custom-workload",
        cluster_names=["cluster-1"],
        manifest=SINGLE_MANIFEST,
        authenticated_session=mock_session,
    )

    assert result.data == {"name": "custom-workload"}
    path, method, req = mock_session.client.invoke_sdk_operation.call_args[0]
    assert path == "/api/v1/workload-placement/"
    assert method == "POST"
    assert req.workspaceName == "ws-1"
    assert req.name == "custom-workload"
    assert req.clusterNames == ["cluster-1"]
    assert len(req.steps) == 1
    assert req.steps[0].name == "custom-server"
    assert req.steps[0].type == "manifest"
    assert req.manifestResources[0].name == "custom-server"
    assert req.manifestResources[0].manifest["kind"] == "Deployment"


def test_create_workload_placement_supports_multi_document_yaml(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(data={})

    create_workload_placement_from_manifest(
        "ws-1",
        "custom-workload",
        ["cluster-1"],
        MULTI_MANIFEST,
        mock_session,
    )

    req = mock_session.client.invoke_sdk_operation.call_args[0][2]
    assert len(req.steps) == 2
    assert len(req.manifestResources) == 2
    assert [resource.manifest["kind"] for resource in req.manifestResources] == [
        "Deployment",
        "Service",
    ]
    # Deployment/foo and Service/foo are legal Kubernetes names, but Workload
    # Placement step names must still be unique.
    assert [step.name for step in req.steps] == ["custom-server", "custom-server-service"]


def test_create_workload_placement_accepts_manifest_dict(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(data={})
    manifest = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {"name": "settings"},
        "data": {"MODE": "prod"},
    }

    create_workload_placement_from_manifest(
        "ws-1", "config-workload", ["cluster-1"], manifest, mock_session
    )
    req = mock_session.client.invoke_sdk_operation.call_args[0][2]
    assert req.manifestResources[0].manifest == manifest


@pytest.mark.parametrize(
    "manifest,error_text",
    [
        ("", "manifest is required"),
        ("apiVersion: v1\nmetadata:\n  name: x", "missing kind"),
        ("apiVersion: v1\nkind: Service", "missing metadata.name"),
        ("- not\n- an\n- object", "must be a Kubernetes object"),
    ],
)
def test_create_workload_placement_rejects_invalid_manifest(mock_session, manifest, error_text):
    with pytest.raises(ValueError, match=error_text):
        create_workload_placement_from_manifest(
            "ws-1", "bad-workload", ["cluster-1"], manifest, mock_session
        )
    mock_session.client.invoke_sdk_operation.assert_not_called()


def test_create_workload_placement_rejects_empty_clusters(mock_session):
    with pytest.raises(ValueError, match="cluster_names"):
        create_workload_placement_from_manifest(
            "ws-1", "workload", [], SINGLE_MANIFEST, mock_session
        )


def test_create_workload_placement_api_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(status_code=500)
    with pytest.raises(UnhandledException):
        create_workload_placement_from_manifest(
            "ws-1", "workload", ["cluster-1"], SINGLE_MANIFEST, mock_session
        )


def test_get_workload_placement(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={"name": "work/load", "status": {"phase": "Ready"}}
    )
    result = get_workload_placement("work/load", mock_session)
    assert result.data["status"]["phase"] == "Ready"
    path, method = mock_session.client.invoke_sdk_operation.call_args[0][:2]
    assert path == "/api/v1/workload-placement/get/work%2Fload"
    assert method == "GET"


def test_list_workload_placements(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data=[{"name": "one"}, {"name": "two"}]
    )
    result = list_workload_placements(mock_session)
    assert len(result.data) == 2
    path, method = mock_session.client.invoke_sdk_operation.call_args[0][:2]
    assert path == "/api/v1/workload-placement/"
    assert method == "GET"


def test_list_workload_placements_by_workspace(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data=[{"name": "one"}]
    )
    result = list_workload_placements_by_workspace("workspace/a", mock_session)
    assert result.data[0]["name"] == "one"
    path, method = mock_session.client.invoke_sdk_operation.call_args[0][:2]
    assert path == "/api/v1/workload-placement/workspace/workspace%2Fa"
    assert method == "GET"


def test_delete_workload_placement(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(data={})
    result = delete_workload_placement("work/load", mock_session)
    assert result.data == {}
    path, method = mock_session.client.invoke_sdk_operation.call_args[0][:2]
    assert path == "/api/v1/workload-placement/work%2Fload"
    assert method == "DELETE"


def test_lifecycle_helpers_raise_on_api_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(status_code=500)
    with pytest.raises(UnhandledException):
        get_workload_placement("x", mock_session)
    with pytest.raises(UnhandledException):
        list_workload_placements(mock_session)
    with pytest.raises(UnhandledException):
        list_workload_placements_by_workspace("ws", mock_session)
    with pytest.raises(UnhandledException):
        delete_workload_placement("x", mock_session)
