from enum import auto
from typing import List, Optional

from egs.util.string_util import serialize


class Resources(object):
    def __init__(self, cpu: str, memory: str):
        self.cpu = cpu
        self.memory = memory

    def __str__(self):
        return serialize(self)


class ModelSpec(object):
    def __init__(
        self,
        model_format_name: str = None,
        storage_uri: str = None,
        args: [str] = None,
        secret: dict = None,
        resources: Resources = None,
    ):
        self.modelName = model_format_name
        self.storageURI = storage_uri
        self.args = args
        self.secret = secret
        self.resources = resources

    def __str__(self):
        return serialize(self)


class GpuSpec(object):
    def __init__(
        self,
        gpu_shape: str,
        instance_type: str,
        memory_per_gpu: int,
        number_of_gpu_nodes: int,
        number_of_gpus: int,
        exit_duration: str,
        priority: int,
    ):
        self.gpuShape = gpu_shape
        self.instanceType = instance_type
        self.memoryPerGPU = memory_per_gpu
        self.numberOfGPUNodes = number_of_gpu_nodes
        self.numberOfGPUs = number_of_gpus
        self.exitDuration = exit_duration
        self.priority = priority

    def __str__(self):
        return serialize(self)


class Autoscaling(object):
    def __init__(
        self,
        max_replicas: int,
        min_replicas: int,
        autoscaling_provider: str,
    ):
        self.maxReplicas = max_replicas
        self.minReplicas = min_replicas
        self.autoscalingProvider = autoscaling_provider

    def __str__(self):
        return serialize(self)


class CreateInferenceEndpointRequest(object):
    def __init__(
        self,
        endpoint_name: str,
        gpu_spec: GpuSpec,
        workspace: str,
        model_spec: Optional[ModelSpec],
        raw_model_spec: Optional[str],
        cluster_precedence: List[str] = [],
        cluster_name: str = "",
        burst: bool = False,
        autoscaling: Optional[Autoscaling] = None,
    ):
        self.clusterName = cluster_name
        self.clusterPrecedence = cluster_precedence
        self.autoscaling = autoscaling
        self.endpointName = endpoint_name
        self.gpuSpec = gpu_spec
        self.workspace = workspace
        self.modelSpec = model_spec
        self.rawModelSpec = raw_model_spec
        self.burst = burst

    def __str__(self):
        return serialize(self)


class CreateInferenceEndpointResponse(object):
    def __init__(self, endpointName: str, *args, **kwargs):
        self.endpoint_name = endpointName

    def __str__(self):
        return serialize(self)
