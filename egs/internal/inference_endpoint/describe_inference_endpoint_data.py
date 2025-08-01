from typing import List

from egs.util.string_util import serialize


class DescribeInferenceEndpointRequest(object):
    def __init__(self, workspace_name: str, endpoint_name: str):
        self.workspace = workspace_name
        self.endpoint = endpoint_name

    def __str__(self):
        return serialize(self)


class GpuRequest(object):
    def __init__(
        self,
        gprName: str,
        gprId: str,
        instanceType: str,
        gpuShape: str,
        numberOfGPUs: int,
        numberOfGPUNodes: int,
        memoryPerGPU: str,
        status: str,
        *args,
        **kwargs
    ):
        self.gprName = gprName
        self.gprId = gprId
        self.instanceType = instanceType
        self.gpuShape = gpuShape
        self.numberOfGPUs = numberOfGPUs
        self.numberOfGPUNodes = numberOfGPUNodes
        self.memoryPerGPU = memoryPerGPU
        self.status = status

    def __str__(self):
        return serialize(self)


class DnsRecord(object):
    def __init__(self, dns: str, type: str, value: str, *args, **kwargs):
        self.dns = dns
        self.type = type
        self.value = value

    def __str__(self):
        return serialize(self)


class InferenceEndpoint(object):
    def __init__(
        self,
        endpointName: str,
        modelName: str,
        status: str,
        endpoint: str,
        clusterName: str,
        namespace: str,
        predictStatus: str,
        ingressStatus: str,
        autoScalingStatus: str,
        tryCommand: List[str],
        dnsRecords: List[DnsRecord],
        gpuRequests: List[GpuRequest],
        *args,
        **kwargs
    ):
        self.endpoint_name = endpointName
        self.model_name = modelName
        self.status = status
        self.endpoint = endpoint
        self.cluster_name = clusterName
        self.namespace = namespace
        self.predict_status = predictStatus
        self.ingress_status = ingressStatus
        self.try_command = tryCommand
        self.dns_records = dnsRecords
        self.gpu_requests = gpuRequests
        self.autoScalingStatus = autoScalingStatus

    def __str__(self):
        return serialize(self)


class DescribeInferenceEndpointResponse(object):
    def __init__(self, endpoint: dict, *args, **kwargs):
        self.endpoint = InferenceEndpoint(**endpoint)

    def __str__(self):
        return serialize(self)

