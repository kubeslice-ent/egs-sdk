from egs.util.string_util import serialize

class CreateGprRequest(object):
    def __init__(
            self,
            request_name: str,
            workspace_name: str,
            cluster_name: str,
            node_count: int,
            gpu_per_node_count: int,
            memory_per_gpu: int,
            instance_type: str,
            gpu_shape: str,
            exit_duration: str,
            priority: int,
            idle_timeout_duration: str,
            enforce_idle_timeout: bool,
            enable_eviction: bool,
            requeue_on_failure: bool,
    ):
        self.gprName = request_name
        self.sliceName = workspace_name
        self.clusterName = cluster_name
        self.numberOfGPUs = gpu_per_node_count
        self.instanceType = instance_type
        self.exitDuration = exit_duration
        self.numberOfGPUNodes = node_count
        self.priority = priority
        self.memoryPerGPU = memory_per_gpu
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
