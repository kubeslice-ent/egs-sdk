from typing import Optional

from egs.util.string_util import serialize


class UpdateGprTemplateRequest:
    def __init__(
        self,
        name: str,
        cluster_name: str,
        number_of_gpus: int,
        instance_type: str,
        exit_duration: str,
        number_of_gpu_nodes: int,
        priority: int,
        gpu_sharing_mode: str,
        memory_per_gpu: int,
        gpu_shape: str,
        enable_eviction: bool,
        requeue_on_failure: bool,
        enforce_idle_timeout: bool,
        idle_timeout_duration: Optional[str] = None,
    ):
        self.name = name
        self.clusterName = cluster_name
        self.numberOfGPUs = number_of_gpus
        self.instanceType = instance_type
        self.exitDuration = exit_duration
        self.numberOfGPUNodes = number_of_gpu_nodes
        self.priority = priority
        self.gpuSharingMode = gpu_sharing_mode
        self.memoryPerGpu = memory_per_gpu
        self.gpuShape = gpu_shape
        self.enableEviction = enable_eviction
        self.requeueOnFailure = requeue_on_failure
        self.enforceIdleTimeOut = enforce_idle_timeout

        if enforce_idle_timeout:
            self.idleTimeOutDuration = idle_timeout_duration

    def __str__(self):
        return serialize(self)


class UpdateGprTemplateResponse:
    def __init__(self, *args, **kwargs):
        pass  # No fields in the response currently

    def __str__(self):
        return "{}"
