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
            gpu_name: str,
            exit_duration: str,
            priority: int,
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
        self.gpuShape = gpu_name

class CreateGprResponse(object):
    def __init__(self, gprId: str, *args, **kwargs):
        self.gpr_id = gprId