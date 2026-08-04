import pytest

from egs.exceptions import UnhandledException
from egs.inference_endpoint import (
    create_inference_endpoint,
    create_inference_endpoint_with_custom_model_spec,
    delete_inference_endpoint,
    describe_inference_endpoint,
    list_inference_endpoints,
)
from egs.internal.inference_endpoint.create_inference_endpoint_data import (
    GpuSpec,
    ModelSpec,
    Resources,
)
from tests.conftest import make_api_response


def _gpu_spec():
    return GpuSpec(
        gpu_shape="A100",
        instance_type="a2",
        memory_per_gpu=40,
        number_of_gpu_nodes=1,
        number_of_gpus=2,
        exit_duration="1h",
        priority=1,
    )


def _model_spec():
    return ModelSpec(
        model_format_name="pytorch",
        storage_uri="s3://bucket/model",
        args=["--port", "8080"],
        secret={"name": "sec"},
        resources=Resources(cpu="2", memory="4Gi"),
    )


def test_list_inference_endpoints_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={
            "endpoints": [
                {
                    "endpointName": "ep-1",
                    "modelName": "m1",
                    "status": "Ready",
                    "endpoint": "http://ep",
                    "clusterName": "c1",
                    "namespace": "ns",
                }
            ]
        }
    )
    result = list_inference_endpoints("ws-1", authenticated_session=mock_session)
    assert len(result.endpoints) == 1
    assert result.endpoints[0].endpoint_name == "ep-1"
    path = mock_session.client.invoke_sdk_operation.call_args[0][0]
    assert path == "/api/v1/inference-endpoint/list?workspace=ws-1"


def test_list_inference_endpoints_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=500
    )
    with pytest.raises(UnhandledException):
        list_inference_endpoints("ws-1", authenticated_session=mock_session)


def test_create_inference_endpoint_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={"endpointName": "ep-1"}
    )
    result = create_inference_endpoint(
        cluster_name="c1",
        endpoint_name="ep-1",
        workspace_name="ws-1",
        standard_model_spec=_model_spec(),
        gpu_spec=_gpu_spec(),
        authenticated_session=mock_session,
    )
    assert result.endpoint_name == "ep-1"
    path, method, req = mock_session.client.invoke_sdk_operation.call_args[0]
    assert path == "/api/v1/inference-endpoint"
    assert method == "POST"
    assert req.modelSpec is not None
    assert req.rawModelSpec is None


def test_create_inference_endpoint_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=400
    )
    with pytest.raises(UnhandledException):
        create_inference_endpoint(
            "c1", "ep-1", "ws-1", _model_spec(), _gpu_spec(), mock_session
        )


def test_create_inference_endpoint_custom_model_spec(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={"endpointName": "ep-2"}
    )
    result = create_inference_endpoint_with_custom_model_spec(
        cluster_name="c1",
        endpoint_name="ep-2",
        workspace_name="ws-1",
        raw_model_spec="custom: yaml",
        gpu_spec=None,
        authenticated_session=mock_session,
    )
    assert result.endpoint_name == "ep-2"
    req = mock_session.client.invoke_sdk_operation.call_args[0][2]
    assert req.rawModelSpec == "custom: yaml"
    assert req.modelSpec is None


def test_create_inference_endpoint_custom_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=500
    )
    with pytest.raises(UnhandledException):
        create_inference_endpoint_with_custom_model_spec(
            "c1", "ep-2", "ws-1", "raw", _gpu_spec(), mock_session
        )


def test_describe_inference_endpoint_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={
            "endpoint": {
                "endpointName": "ep-1",
                "modelName": "m1",
                "status": "Ready",
                "endpoint": "http://ep",
                "clusterName": "c1",
                "namespace": "ns",
                "predictStatus": "ok",
                "ingressStatus": "ok",
                "tryCommand": ["curl"],
                "dnsRecords": [{"dns": "a", "type": "A", "value": "1.1.1.1"}],
                "gpuRequests": [
                    {
                        "gprName": "g1",
                        "gprId": "id1",
                        "instanceType": "a2",
                        "gpuShape": "A100",
                        "numberOfGPUs": 1,
                        "numberOfGPUNodes": 1,
                        "memoryPerGPU": "40",
                        "status": "Running",
                    }
                ],
            }
        }
    )
    result = describe_inference_endpoint(
        "ws-1", "ep-1", "c1", authenticated_session=mock_session
    )
    assert result.endpoint.endpoint_name == "ep-1"
    path = mock_session.client.invoke_sdk_operation.call_args[0][0]
    assert "workspace=ws-1" in path
    assert "endpoint=ep-1" in path
    assert "cluster=c1" in path


def test_describe_inference_endpoint_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=404
    )
    with pytest.raises(UnhandledException):
        describe_inference_endpoint(
            "ws-1", "ep-1", "c1", authenticated_session=mock_session
        )


def test_delete_inference_endpoint_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(data={})
    result = delete_inference_endpoint(
        "ws-1", "ep-1", "c1", authenticated_session=mock_session
    )
    assert result is not None
    path, method, req = mock_session.client.invoke_sdk_operation.call_args[0]
    assert method == "DELETE"
    assert req.workspace == "ws-1"
    assert req.endpoint == "ep-1"
    assert req.cluster == "c1"


def test_delete_inference_endpoint_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=500
    )
    with pytest.raises(UnhandledException):
        delete_inference_endpoint(
            "ws-1", "ep-1", "c1", authenticated_session=mock_session
        )
