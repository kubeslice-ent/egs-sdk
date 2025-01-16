from egs.util.string_util import serialize

class InventoryUsage(object):
    def __init__(
            self,
            nodeName: [str],
            instanceType: str,
            memory: int,
            totalGpus: int,
            gpuShape: str
    ):
        self.node_name = nodeName
        self.instance_type = instanceType
        self.memory = memory
        self.total_gpus = totalGpus
        self.gpu_shape = gpuShape

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
