from egs.util.string_util import serialize

class InventoryUsage(object):
    def __init__(
            self,
            instanceType: str,
            gpuShape: str,
            memoryPerGpu: int,
            gpuPerNode: int,
            totalGpuNodes: int,
            clusterName: str,
            *args, **kwargs
    ):
        self.instance_type = instanceType
        self.gpu_shape = gpuShape
        self.memory_per_gpu = memoryPerGpu
        self.gpu_per_node = gpuPerNode
        self.total_gpu_nodes = totalGpuNodes
        self.cluster_name = clusterName

    def __str__(self):
        return serialize(self)


class ListWorkspaceInventoryUsageResponse(object):
    def __init__(self, items: [InventoryUsage], *args, **kwargs):
        iu = []
        for i in items:
            iu.append(InventoryUsage(**i))
        self.workspace_inventory = iu

    def __str__(self):
        return serialize(self)
