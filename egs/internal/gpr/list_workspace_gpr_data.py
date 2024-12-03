class ListWorkspaceGprRequest(object):
    def __init__(self, workspace_name: str):
        self.workspace_name = workspace_name


class GprStatus(object):
    def __init__(
            self,
            provisioning_status: str,
            failure_reason: str,
            num_gpus_allocated: int,
            start_timestamp: str,
            completion_timestamp: str,
            cost: str,
            nodes: [str],
            internal_state: str,
            retry_count: int,
            delayed_count: int,
    ):
        self.provisioning_status = provisioning_status
        self.failure_reason = failure_reason
        self.num_gpus_allocated = num_gpus_allocated
        self.start_timestamp = start_timestamp
        self.completion_timestamp = completion_timestamp
        self.cost = cost
        self.nodes = nodes
        self.internal_state = internal_state
        self.retry_count = retry_count
        self.delayed_count = delayed_count


class GprData(object):
    def __init__(
            self,
            gpr_id: str,
            slice_name: str,
            cluster_name: str,
            number_of_gpus: int,
            number_of_gpu_nodes: int,
            instance_type: str,
            memory_per_gpu: int,
            priority: int,
            gpu_sharing_mode: str,
            estimated_start_time: str,
            estimated_wait_time: str,
            exit_duration: str,
            early_release: bool,
            gpr_name: str,
            gpu_shape: str,
            multi_node: bool,
            dedicated_nodes: bool,
            enable_rdma: bool,
            enable_secondary_network: bool,
            status: GprStatus,
    ):
        self.gpr_id = gpr_id
        self.slice_name = slice_name
        self.cluster_name = cluster_name
        self.number_of_gpus = number_of_gpus
        self.number_of_gpu_nodes = number_of_gpu_nodes
        self.instance_type = instance_type
        self.memory_per_gpu = memory_per_gpu
        self.priority = priority
        self.gpu_sharing_mode = gpu_sharing_mode
        self.estimated_start_time = estimated_start_time
        self.estimated_wait_time = estimated_wait_time
        self.exit_duration = exit_duration
        self.early_release = early_release
        self.gpr_name = gpr_name
        self.gpu_shape = gpu_shape
        self.multi_node = multi_node
        self.dedicated_nodes = dedicated_nodes
        self.enable_rdma = enable_rdma
        self.enable_secondary_network = enable_secondary_network
        self.status = status

class ListWorkspaceGprResponse(object):
    def __init__(self, items: [GprData]):
        self.items = items

class GetGprByIdRequest(object):
    def __init__(self, gpr_id: str):
        self.gpr_id = gpr_id