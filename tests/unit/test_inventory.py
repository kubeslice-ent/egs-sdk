import pytest

from egs.exceptions import UnhandledException
from egs.inventory_operations import inventory, workspace_inventory
from tests.conftest import make_api_response


def test_inventory_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={
            "managedNodes": [
                {
                    "gpuNodeName": "node-1",
                    "gpuModelName": "A100",
                    "instanceType": "a2",
                    "clusterName": "c1",
                    "memory": 40,
                    "gpuCount": 2,
                    "availableGPUs": 1,
                    "allocation": [
                        {
                            "gprName": "g1",
                            "sliceName": "ws-1",
                            "totalGPUsAllocated": 1,
                            "allocationTimeStamp": {"seconds": "1", "nanos": 0},
                        }
                    ],
                    "gpuSlicingProfile": [
                        {
                            "profileName": "p1",
                            "memory": "20",
                            "totalGpus": 2,
                            "deviceName": "A100",
                            "availableGpus": 1,
                            "memoryPerGpu": "20",
                            "gpusPerNode": 2,
                        }
                    ],
                }
            ],
            "unmanagedNodes": [],
        }
    )
    result = inventory(authenticated_session=mock_session)
    assert len(result.managed_nodes) == 1
    assert result.managed_nodes[0].gpu_node_name == "node-1"
    assert result.managed_nodes[0].allocation[0].gpr_name == "g1"
    assert result.managed_nodes[0].gpu_slicing_profile[0].profile_name == "p1"
    path, method = mock_session.client.invoke_sdk_operation.call_args[0][:2]
    assert path == "/api/v1/inventory/list"
    assert method == "GET"


def test_inventory_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=500
    )
    with pytest.raises(UnhandledException):
        inventory(authenticated_session=mock_session)


def test_workspace_inventory_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={
            "items": [
                {
                    "instanceType": "a2",
                    "gpuShape": "A100",
                    "memoryPerGpu": 40,
                    "gpuPerNode": 2,
                    "totalGpuNodes": 3,
                    "clusterName": "c1",
                }
            ]
        }
    )
    result = workspace_inventory("ws-1", authenticated_session=mock_session)
    assert len(result.workspace_inventory) == 1
    assert result.workspace_inventory[0].cluster_name == "c1"
    path = mock_session.client.invoke_sdk_operation.call_args[0][0]
    assert path == "/api/v1/inventory?sliceName=ws-1"


def test_workspace_inventory_error(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=404
    )
    with pytest.raises(UnhandledException):
        workspace_inventory("ws-1", authenticated_session=mock_session)
