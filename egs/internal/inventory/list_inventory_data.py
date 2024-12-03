class ListInventoryRequest(object):
    def __init__(self):
        pass


class Inventory(object):
    def __init__(
            self,
            gpuNodeName: str,
            gpuShape: str,
            gpuModelName: str,
            instanceType: str,
            clusterName: str,
            memory: int,
            gpuCount: int,
            gpuTempThreshold: str,
            gpuPowerThreshold: str,
            cloudProvider: str,
            region: str,
            nodeHealth: str,
            gpuNodeStatus: str,
            *args, **kwargs
    ):
        self.gpu_node_name = gpuNodeName
        self.gpu_shape = gpuShape
        self.gpu_model_name = gpuModelName
        self.instance_type = instanceType
        self.cluster_name = clusterName
        self.memory = memory
        self.gpu_count = gpuCount
        self.gpu_temp_threshold = gpuTempThreshold
        self.gpu_power_threshold = gpuPowerThreshold
        self.cloud_provider = cloudProvider
        self.region = region
        self.node_health = nodeHealth
        self.gpu_node_status = gpuNodeStatus


class ListInventoryResponse(object):
    def __init__(self, items: [Inventory], *args, **kwargs):
        iu = []
        for i in items:
            iu.append(Inventory(**i))
        self.items = iu
