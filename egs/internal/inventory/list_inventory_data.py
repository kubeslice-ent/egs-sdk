from egs.util.string_util import serialize

class ListInventoryRequest(object):
    def __init__(self):
        pass


class AllocationTime(object):
    def __init__(
            self,
            seconds: str,
            nanos: int,
            *args, **kwargs
    ):
        self.seconds = seconds
        self.nanos = nanos

    def __str__(self):
        return serialize(self)

class Allocation(object):
    def __init__(
            self,
            gprName: str,
            sliceName: str,
            totalGPUsAllocated: int,
            allocationTimeStamp: AllocationTime,
            *args, **kwargs
    ):
        self.gpr_name = gprName
        self.slice_name = sliceName
        self.total_gpus_allocated = totalGPUsAllocated
        self.allocation_timestamp = allocationTimeStamp

    def __str__(self):
        return serialize(self)


# type GPUSlicingInfo struct {
#     ProfileName   string `json:"profileName"`
# Memory        string `json:"memory"`
# TotalGPUs     int    `json:"totalGpus"`
# DeviceName    string `json:"deviceName"`
# AvailableGPUs int    `json:"availableGpus"`
# MemoryPerGPU  string `json:"memoryPerGpu"`
# GpusPerNode   int    `json:"gpusPerNode"`
# }

class GpuSlicingProfile(object):
    def __init__(
            self,
            profileName: str,
            memory: str,
            totalGpus: int,
            deviceName: str,
            availableGpus: int,
            memoryPerGpu: str,
            gpusPerNode: int,
            *args, **kwargs
    ):
        self.profile_name = profileName
        self.memory = memory
        self.total_gpus = totalGpus
        self.device_name = deviceName
        self.available_gpus = availableGpus
        self.memory_per_gpu = memoryPerGpu
        self.gpus_per_node = gpusPerNode

    def __str__(self):
        return serialize(self)


class Inventory(object):
    def __init__(
            self,
            gpuNodeName: str = None,
            gpuShape: str = None,
            gpuModelName: str = None,
            instanceType: str = None,
            clusterName: str = None,
            memory: int = None,
            gpuCount: int = None,
            gpuTempThreshold: str = None,
            gpuPowerThreshold: str = None,
            cloudProvider: str = None,
            region: str = None,
            nodeHealth: str = None,
            gpuNodeStatus: str = None,
            cloud: str = None,
            allocation: [Allocation] = None,
            gpuSlicingProfile: [GpuSlicingProfile] = None,
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
        self.cloud = cloud
        self.allocation = allocation
        self.gpu_slicing_profile = gpuSlicingProfile

    def __str__(self):
        return serialize(self)


class ListInventoryResponse(object):
    def __init__(
            self,
            managedNodes: [Inventory],
            unmanagedNodes: [Inventory],
            *args, **kwargs):
        m = []
        for i in managedNodes:
            m.append(Inventory(**i))

        u = []
        for i in unmanagedNodes:
            u.append(Inventory(**i))
        self.managed_nodes = m
        self.unmanaged_nodes = u
        # self.managed_nodes = managedNodes
        # self.unmanaged_nodes = unmanagedNodes

    def __str__(self):
        return serialize(self)
