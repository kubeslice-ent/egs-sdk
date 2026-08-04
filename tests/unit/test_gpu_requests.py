import pytest

from egs.exceptions import GpuAlreadyProvisioned, GpuAlreadyReleased, UnhandledException
from egs.gpu_requests import (
    cancel_gpu_request,
    gpu_request_status,
    gpu_request_status_for_workspace,
    release_gpu,
    request_gpu,
    request_gpu_with_auto_cluster,
    request_gpu_with_auto_gpu_selection,
    request_gpu_with_auto_selection,
    request_gpu_with_manual_selection,
    update_gpu_request_name,
    update_gpu_request_priority,
)
from tests.conftest import make_api_response

BASE_KWARGS = dict(
    request_name="req-1",
    workspace_name="ws-1",
    node_count=1,
    gpu_per_node_count=2,
    memory_per_gpu=40,
    exit_duration="1h",
    priority=5,
    idle_timeout_duration="30m",
    enforce_idle_timeout=True,
)


def test_request_gpu_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={"gprId": "gpr-1"}
    )
    gpr_id = request_gpu(
        **BASE_KWARGS,
        cluster_name="c1",
        instance_type="a2",
        gpu_shape="A100",
        authenticated_session=mock_session,
    )
    assert gpr_id == "gpr-1"
    path, method, req = mock_session.client.invoke_sdk_operation.call_args[0]
    assert path == "/api/v1/gpr"
    assert method == "POST"
    assert req.gprName == "req-1"
    assert req.sliceName == "ws-1"


def test_request_gpu_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=500
    )
    with pytest.raises(UnhandledException):
        request_gpu(**BASE_KWARGS, authenticated_session=mock_session)


def test_request_gpu_with_auto_selection(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={"gprId": "gpr-auto"}
    )
    gpr_id = request_gpu_with_auto_selection(
        **BASE_KWARGS, authenticated_session=mock_session
    )
    assert gpr_id == "gpr-auto"
    req = mock_session.client.invoke_sdk_operation.call_args[0][2]
    assert req.enableAutoClusterSelection is True
    assert req.enableAutoGpuSelection is True


def test_request_gpu_with_auto_selection_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=400
    )
    with pytest.raises(UnhandledException):
        request_gpu_with_auto_selection(
            **BASE_KWARGS, authenticated_session=mock_session
        )


def test_request_gpu_with_auto_gpu_selection(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={"gprId": "gpr-gpu"}
    )
    gpr_id = request_gpu_with_auto_gpu_selection(
        **BASE_KWARGS,
        preferred_clusters=["c1", "c2"],
        authenticated_session=mock_session,
    )
    assert gpr_id == "gpr-gpu"
    req = mock_session.client.invoke_sdk_operation.call_args[0][2]
    assert req.enableAutoGpuSelection is True
    assert req.enableAutoClusterSelection is False
    assert req.preferredClusters == ["c1", "c2"]


def test_request_gpu_with_auto_gpu_selection_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=500
    )
    with pytest.raises(UnhandledException):
        request_gpu_with_auto_gpu_selection(
            **BASE_KWARGS,
            preferred_clusters=["c1"],
            authenticated_session=mock_session,
        )


def test_request_gpu_with_auto_cluster(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={"gprId": "gpr-cluster"}
    )
    gpr_id = request_gpu_with_auto_cluster(
        **BASE_KWARGS,
        instance_type="a2-highgpu-2g",
        gpu_shape="A100",
        authenticated_session=mock_session,
    )
    assert gpr_id == "gpr-cluster"
    req = mock_session.client.invoke_sdk_operation.call_args[0][2]
    assert req.enableAutoClusterSelection is True
    assert req.enableAutoGpuSelection is False
    assert req.instanceType == "a2-highgpu-2g"


def test_request_gpu_with_auto_cluster_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=500
    )
    with pytest.raises(UnhandledException):
        request_gpu_with_auto_cluster(
            **BASE_KWARGS,
            instance_type="a2",
            gpu_shape="A100",
            authenticated_session=mock_session,
        )


def test_request_gpu_with_manual_selection(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={"gprId": "gpr-manual"}
    )
    gpr_id = request_gpu_with_manual_selection(
        **BASE_KWARGS,
        cluster_name="c1",
        instance_type="a2",
        gpu_shape="A100",
        authenticated_session=mock_session,
    )
    assert gpr_id == "gpr-manual"
    req = mock_session.client.invoke_sdk_operation.call_args[0][2]
    assert req.enableAutoClusterSelection is False
    assert req.enableAutoGpuSelection is False
    assert req.clusterName == "c1"
    assert req.preferredClusters == ["c1"]


def test_request_gpu_with_manual_selection_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=500
    )
    with pytest.raises(UnhandledException):
        request_gpu_with_manual_selection(
            **BASE_KWARGS,
            cluster_name="c1",
            instance_type="a2",
            gpu_shape="A100",
            authenticated_session=mock_session,
        )


def test_cancel_gpu_request_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response()
    assert cancel_gpu_request("gpr-1", authenticated_session=mock_session) is None
    path, method, req = mock_session.client.invoke_sdk_operation.call_args[0]
    assert method == "DELETE"
    assert req.gprId == "gpr-1"


def test_cancel_gpu_request_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=409
    )
    with pytest.raises(GpuAlreadyProvisioned):
        cancel_gpu_request("gpr-1", authenticated_session=mock_session)


def test_update_gpu_request_priority_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response()
    assert (
        update_gpu_request_priority("gpr-1", 9, authenticated_session=mock_session)
        is None
    )
    req = mock_session.client.invoke_sdk_operation.call_args[0][2]
    assert req.priority == 9


def test_update_gpu_request_priority_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=409
    )
    with pytest.raises(GpuAlreadyProvisioned):
        update_gpu_request_priority("gpr-1", 9, authenticated_session=mock_session)


def test_update_gpu_request_name_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response()
    assert (
        update_gpu_request_name("gpr-1", "new-name", authenticated_session=mock_session)
        is None
    )
    req = mock_session.client.invoke_sdk_operation.call_args[0][2]
    assert req.gprName == "new-name"


def test_update_gpu_request_name_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=409
    )
    with pytest.raises(GpuAlreadyProvisioned):
        update_gpu_request_name(
            "gpr-1", "new-name", authenticated_session=mock_session
        )


def test_release_gpu_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response()
    assert release_gpu("gpr-1", authenticated_session=mock_session) is None
    req = mock_session.client.invoke_sdk_operation.call_args[0][2]
    assert req.gprId == "gpr-1"
    assert req.earlyRelease is True


def test_release_gpu_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=409
    )
    with pytest.raises(GpuAlreadyReleased):
        release_gpu("gpr-1", authenticated_session=mock_session)


def test_gpu_request_status_success(mock_session, gpr_status_payload):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data=gpr_status_payload
    )
    result = gpu_request_status("gpr-123", authenticated_session=mock_session)
    assert result.gpr_id == "gpr-123"
    assert result.status.provisioning_status == "Running"
    path = mock_session.client.invoke_sdk_operation.call_args[0][0]
    assert path == "/api/v1/gpr?gprId=gpr-123"


def test_gpu_request_status_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=404
    )
    with pytest.raises(UnhandledException):
        gpu_request_status("gpr-123", authenticated_session=mock_session)


def test_gpu_request_status_for_workspace_success(mock_session, gpr_status_payload):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={"items": [gpr_status_payload]}
    )
    result = gpu_request_status_for_workspace(
        "ws-1", authenticated_session=mock_session
    )
    assert len(result.items) == 1
    assert result.items[0].gpr_name == "req-1"
    path = mock_session.client.invoke_sdk_operation.call_args[0][0]
    assert path == "/api/v1/gpr/list?sliceName=ws-1"


def test_gpu_request_status_for_workspace_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=500
    )
    with pytest.raises(UnhandledException):
        gpu_request_status_for_workspace("ws-1", authenticated_session=mock_session)
