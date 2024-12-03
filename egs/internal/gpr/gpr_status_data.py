class GpuRequestStatus(object):
    def __init__(
            self,
            provisioningStatus: str,
            failureReason: str,
            numGpusAllocated: str,
            startTimestamp: str,
            completionTimestamp: str,
            cost: str,
            nodes: str,
            internalState: str,
            retryCount: str,
            delayedCount: str,
            *args, **kwargs
    ):
        self.provisioning_status = provisioningStatus
        self.failure_reason = failureReason
        self.num_gpus_allocated = numGpusAllocated
        self.start_timestamp = startTimestamp
        self.completion_timestamp = completionTimestamp
        self.cost = cost
        self.nodes = nodes
        self.internal_state = internalState
        self.retry_count = retryCount
        self.delayed_count = delayedCount

class GpuRequestData(object):
    def __init__(
            self,
            gprId: str,
            sliceName: str,
            clusterName: str,
            numberOfGPUs: int,
            numberOfGPUNodes: int,
            instanceType: str,
            memoryPerGPU: int,
            priority: int,
            gpuSharingMode: str,
            estimatedStartTime: str,
            estimatedWaitTime: str,
            exitDuration: str,
            earlyRelease: bool,
            gprName: str,
            gpuShape: str,
            multiNode: bool,
            dedicatedNodes: bool,
            enableRDMA: bool,
            enableSecondaryNetwork: bool,
            status: dict,
            *args, **kwargs
    ):
        self.gpr_id = gprId
        self.slice_name = sliceName
        self.cluster_name = clusterName
        self.number_of_gp_us = numberOfGPUs
        self.number_of_gpu_nodes = numberOfGPUNodes
        self.instance_type = instanceType
        self.memory_per_gpu = memoryPerGPU
        self.priority = priority
        self.gpu_sharing_mode = gpuSharingMode
        self.estimated_start_time = estimatedStartTime
        self.estimated_wait_time = estimatedWaitTime
        self.exit_duration = exitDuration
        self.early_release = earlyRelease
        self.gpr_name = gprName
        self.gpu_shape = gpuShape
        self.multi_node = multiNode
        self.dedicated_nodes = dedicatedNodes
        self.enable_rdma = enableRDMA
        self.enable_secondary_network = enableSecondaryNetwork
        self.status = GpuRequestStatus(**status)

class WorkspaceGpuRequestDataResponse(object):
    def __init__(
            self,
            items: [GpuRequestData],
            *args, **kwargs
    ):
        iu = []
        for i in items:
            iu.append(GpuRequestData(**i))
        self.items = iu