# tests/test_gpu_requests.py
import pytest
import uuid
import egs
from egs.exceptions import UnhandledException
from egs.internal.gpr.gpr_status_data import WorkspaceGpuRequestDataResponse, GpuRequestData

@pytest.mark.skip_gpu
def test_request_and_cancel_gpu(auth_session, workspace):
    """Test requesting and cancelling a GPU request in the workspace"""
    ws_name, clusters, namespaces, username, email = workspace
    cluster = clusters[0]

    # Determine available GPU node specs from inventory
    inv = egs.inventory(authenticated_session=auth_session)
    gpu_nodes = [n for n in inv.managed_nodes if n.cluster_name == cluster and n.gpu_count > 0]
    if not gpu_nodes:
        pytest.skip(f"No GPU nodes available in cluster {cluster}")
    node = gpu_nodes[0]
    # Use the instance type and GPU shape from inventory
    instance_type = node.instance_type
    gpu_shape = node.gpu_shape
    # Calculate memory per GPU if possible
    memory_per_gpu = node.memory // node.gpu_count if node.memory and node.gpu_count else 1
    # Submit a GPU request with valid parameters
    request_name = f"gpr-{uuid.uuid4().hex[:6]}"
    request_id = egs.request_gpu(
        request_name=request_name,
        workspace_name=ws_name,
        cluster_name=cluster,
        node_count=1,
        gpu_per_node_count=1,
        memory_per_gpu=memory_per_gpu,
        instance_type=instance_type,
        gpu_shape=gpu_shape,
        exit_duration="5m",
        priority=1,
        idle_timeout_duration="5m",
        enforce_idle_timeout=True,
        enable_eviction=False,
        requeue_on_failure=False,
        authenticated_session=auth_session
    )
    assert isinstance(request_id, str)

    # Check status for the GPU request
    status = egs.gpu_request_status(request_id, authenticated_session=auth_session)
    assert isinstance(status, GpuRequestData)
    assert status.gpr_id == request_id

    # Cancel the GPU request
    egs.cancel_gpu_request(request_id, authenticated_session=auth_session)

    # Verify that listing workspace GPU requests returns a valid response
    ws_status = egs.gpu_request_status_for_workspace(ws_name, authenticated_session=auth_session)
    assert isinstance(ws_status, WorkspaceGpuRequestDataResponse)
    # Note: specific request presence may vary after cancellation 