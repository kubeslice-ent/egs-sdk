from typing import Optional
from egs.util.string_util import serialize

class CreateGprTemplateRequest:
    def __init__(
        self,
        name: str,
        cluster_name: str,
        gpu_per_node_count: int,
        num_gpu_nodes: int,
        memory_per_gpu: int,
        gpu_shape: str,
        instance_type: str,
        exit_duration: str,
        priority: int,
        enforce_idle_timeout: bool,
        enable_eviction: bool,
        requeue_on_failure: bool,
        idle_timeout_duration: Optional[str] = None,
    ):
        self.name = name
        self.clusterName = cluster_name
        self.numberOfGPUs = gpu_per_node_count  # Matches API field
        self.numberOfGPUNodes = num_gpu_nodes  # Matches API field
        self.memoryPerGpu = memory_per_gpu
        self.gpuShape = gpu_shape
        self.instanceType = instance_type
        self.exitDuration = exit_duration
        self.priority = priority
        self.enforceIdleTimeOut = enforce_idle_timeout
        self.enableEviction = enable_eviction
        self.requeueOnFailure = requeue_on_failure

        if enforce_idle_timeout:
            self.idleTimeOutDuration = idle_timeout_duration

    def __str__(self):
        return serialize(self)


class CreateGprTemplateResponse:
    def __init__(self, gprTemplateName: str):
        self.gpr_template_name = gprTemplateName  # Matches API field

    def __str__(self):
        return serialize(self)
