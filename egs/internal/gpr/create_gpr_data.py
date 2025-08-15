from typing import List, Optional

from egs.util.string_util import serialize


class CreateGprRequest(object):
    def __init__(
        self,
        request_name: str,
        workspace_name: str,
        node_count: int,
        gpu_per_node_count: int,
        memory_per_gpu: int,
        exit_duration: str,
        priority: int,
        idle_timeout_duration: str,
        enforce_idle_timeout: bool,
        cluster_name: str = "",
        instance_type: str = "",
        gpu_shape: str = "",
        enable_eviction: Optional[bool] = None,
        requeue_on_failure: Optional[bool] = None,
        preferred_clusters: Optional[List[str]] = None,
        enable_auto_cluster_selection: bool = False,
        enable_auto_gpu_selection: bool = False,
    ):
        self.gprName = request_name
        self.sliceName = workspace_name
        self.clusterName = cluster_name
        self.preferredClusters = preferred_clusters
        self.enableAutoClusterSelection = enable_auto_cluster_selection
        self.enableAutoGpuSelection = enable_auto_gpu_selection
        self.numberOfGPUs = gpu_per_node_count
        self.instanceType = instance_type
        self.exitDuration = exit_duration
        self.numberOfGPUNodes = node_count
        self.priority = priority
        self.memoryPerGpu = memory_per_gpu
        self.gpuShape = gpu_shape
        self.idleTimeOutDuration = idle_timeout_duration
        self.enforceIdleTimeOut = enforce_idle_timeout
        self.enableEviction = enable_eviction
        self.requeueOnFailure = requeue_on_failure

    def __str__(self):
        return serialize(self)


class CreateGprResponse(object):
    def __init__(self, gprId: str, *args, **kwargs):
        self.gpr_id = gprId

    def __str__(self):
        return serialize(self)
