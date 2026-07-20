from unittest.mock import MagicMock

import pytest

from egs.authenticated_session import AuthenticatedSession
from egs.internal.client.api_reponse import ApiResponse


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def mock_session(mock_client):
    return AuthenticatedSession(mock_client, sdk_default=False)


def make_api_response(status_code=200, data=None, message="ok", status="success", error=None):
    return ApiResponse(
        status=status,
        message=message,
        statusCode=status_code,
        data=data if data is not None else {},
        error=error,
    )


@pytest.fixture
def api_response_factory():
    return make_api_response


@pytest.fixture
def gpr_status_payload():
    return {
        "gprId": "gpr-123",
        "sliceName": "ws-1",
        "clusterName": "cluster-1",
        "numberOfGPUs": 2,
        "numberOfGPUNodes": 1,
        "instanceType": "a2-highgpu-2g",
        "memoryPerGPU": 40,
        "priority": 1,
        "gpuSharingMode": "none",
        "estimatedStartTime": "now",
        "estimatedWaitTime": "0",
        "exitDuration": "1h",
        "earlyRelease": False,
        "gprName": "req-1",
        "gpuShape": "A100",
        "multiNode": False,
        "dedicatedNodes": True,
        "enableRDMA": False,
        "enableSecondaryNetwork": False,
        "status": {
            "provisioningStatus": "Running",
            "failureReason": "",
            "numGpusAllocated": "2",
            "startTimestamp": "t0",
            "completionTimestamp": "",
            "cost": "0",
            "nodes": "node-1",
            "internalState": "active",
            "retryCount": "0",
            "delayedCount": "0",
        },
    }


@pytest.fixture
def gpr_template_payload():
    return {
        "name": "tpl-1",
        "clusterName": "cluster-1",
        "numberOfGPUs": 2,
        "numberOfGPUNodes": 1,
        "memoryPerGpu": 40,
        "gpuShape": "A100",
        "instanceType": "a2-highgpu-2g",
        "exitDuration": "1h",
        "priority": 5,
        "enforceIdleTimeOut": True,
        "enableEviction": False,
        "requeueOnFailure": True,
        "idleTimeOutDuration": "30m",
    }
