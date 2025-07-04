from egs.util.string_util import serialize
from typing import List, Optional

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
            allocationTimeStamp: dict,
            *args, **kwargs
    ):
        self.gpr_name = gprName
        self.slice_name = sliceName
        self.total_gpus_allocated = totalGPUsAllocated
        self.allocation_timestamp = AllocationTime(**allocationTimeStamp)

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
            allocation: Optional[List[dict]] = None,
            gpuSlicingProfile: Optional[List[dict]] = None,
            *args, **kwargs
    ):
        self.gpu_node_name = gpuNodeName
        self.gpu_shape = gpuModelName
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
        self.allocation = [Allocation(**a) for a in allocation] if allocation else None
        self.gpu_slicing_profile = [GpuSlicingProfile(**gsp) for gsp in gpuSlicingProfile] if gpuSlicingProfile else None

    def __str__(self):
        return serialize(self)


class ListInventoryResponse(object):
    def __init__(
            self,
            managedNodes: List[dict],
            unmanagedNodes: List[dict],
            *args, **kwargs):

        self.managed_nodes = [Inventory(**mn) for mn in managedNodes]
        self.unmanaged_nodes = [Inventory(**umn) for umn in unmanagedNodes]
        
    def __str__(self):
        return serialize(self)
