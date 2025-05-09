# tests/test_inference_endpoint.py
import pytest
import uuid
import egs

from egs.internal.inference_endpoint.list_inference_endpoint_data import ListInferenceEndpointResponse
from egs.internal.inference_endpoint.create_inference_endpoint_data import (
    ModelSpec, GpuSpec, Resources, CreateInferenceEndpointResponse
)
from egs.internal.inference_endpoint.delete_inference_endpoint_data import DeleteInferenceEndpointResponse

@pytest.mark.skip_inference
def test_list_inference_endpoints(auth_session, workspace):
    ws_name, clusters, namespaces, username, email = workspace
    resp = egs.list_inference_endpoint(ws_name, authenticated_session=auth_session)
    assert isinstance(resp, ListInferenceEndpointResponse)
    assert hasattr(resp, 'endpoints')

@pytest.mark.skip_inference
def test_create_and_delete_inference_endpoint(auth_session, workspace):
    ws_name, clusters, namespaces, username, email = workspace
    cluster = clusters[0]
    endpoint_name = f"ep-{uuid.uuid4().hex[:6]}"

    # Prepare model spec
    resources = Resources(cpu="100m", memory="128Mi")
    model_spec = ModelSpec(
        model_format_name="test-model",
        storage_uri="s3://test-bucket/model",
        args=[],
        secret={},
        resources=resources
    )
    # Determine valid GPU spec from inventory
    inv = egs.inventory(authenticated_session=auth_session)
    gpu_nodes = [n for n in inv.managed_nodes if n.cluster_name == cluster and n.gpu_count > 0]
    if not gpu_nodes:
        pytest.skip(f"No GPU nodes available in cluster {cluster}")
    node = gpu_nodes[0]
    instance_type = node.instance_type
    gpu_shape = node.gpu_shape
    memory_per_gpu = node.memory // node.gpu_count if node.memory and node.gpu_count else 1
    gpu_spec = GpuSpec(
        gpu_shape=gpu_shape,
        instance_type=instance_type,
        memory_per_gpu=memory_per_gpu,
        number_of_gpu_nodes=1,
        number_of_gpus=1,
        exit_duration="1m",
        priority=1
    )

    # Create endpoint
    resp = egs.create_inference_endpoint(
        cluster_name=cluster,
        endpoint_name=endpoint_name,
        workspace_name=ws_name,
        standard_model_spec=model_spec,
        gpu_spec=gpu_spec,
        authenticated_session=auth_session
    )
    assert isinstance(resp, CreateInferenceEndpointResponse)

    # Verify endpoint appears in list
    list_resp = egs.list_inference_endpoint(ws_name, authenticated_session=auth_session)
    assert any(ep.endpoint_name == endpoint_name for ep in list_resp.endpoints)

    # Delete endpoint
    del_resp = egs.delete_inference_endpoint(
        workspace_name=ws_name,
        endpoint_name=endpoint_name,
        cluster_name=cluster,
        authenticated_session=auth_session
    )
    assert isinstance(del_resp, DeleteInferenceEndpointResponse) 