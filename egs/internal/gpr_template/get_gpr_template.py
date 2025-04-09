from typing import Optional

from egs.util.string_util import serialize


class GetGprTemplateResponse:
    """Response model for retrieving a GPR template."""

    def __init__(
        self,
        name: str,
        namespace: str,
        clusterName: str,
        numberOfGPUs: int,
        numberOfGPUNodes: int,
        memoryPerGpu: int,
        gpuShape: str,
        instanceType: str,
        exitDuration: str,
        # gpuSharingMode: str,
        priority: int,
        enforceIdleTimeOut: bool,
        enableEviction: bool,
        requeueOnFailure: bool,
        idleTimeOutDuration: Optional[str] = None,
        **kwargs,  # To handle extra fields gracefully
    ):
        self.name = name
        self.namespace = namespace
        self.cluster_name = clusterName
        self.number_of_gpus = numberOfGPUs
        self.number_of_gpu_nodes = numberOfGPUNodes
        self.memory_per_gpu = memoryPerGpu
        self.gpu_shape = gpuShape
        self.instance_type = instanceType
        self.exit_duration = exitDuration
        # self.gpu_sharing_mode = gpuSharingMode
        self.priority = priority
        self.enforce_idle_timeout = enforceIdleTimeOut
        self.enable_eviction = enableEviction
        self.requeue_on_failure = requeueOnFailure
        if self.enforce_idle_timeout:
            self.idle_timeout_duration = idleTimeOutDuration

    def __str__(self):
        return serialize(self)
