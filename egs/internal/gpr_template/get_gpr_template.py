from egs.util.string_util import serialize


class GetGprTemplateRequest:
    """Request model for retrieving a GPR template."""

    def __init__(self, gpr_template_name: str):
        self.gprTemplateName = gpr_template_name  # Matches API field

    def __str__(self):
        return serialize(self)


class GetGprTemplateResponse:
    """Response model for retrieving a GPR template."""

    def __init__(
        self,
        name: str,
        namespace: str,
        clusterName: str,
        exitDuration: str,
        gpuShape: str,
        gpuSharingMode: str,
        instanceType: str,
        memoryPerGpu: int,
        numberOfGPUNodes: int,
        numberOfGPUs: int,
        priority: int,
        requeueOnFailure: bool,
        **kwargs,  # To handle extra fields gracefully
    ):
        self.name = name
        self.namespace = namespace
        self.cluster_name = clusterName
        self.exit_duration = exitDuration
        self.gpu_shape = gpuShape
        self.gpu_sharing_mode = gpuSharingMode
        self.instance_type = instanceType
        self.memory_per_gpu = memoryPerGpu
        self.number_of_gpu_nodes = numberOfGPUNodes
        self.number_of_gpus = numberOfGPUs
        self.priority = priority
        self.requeue_on_failure = requeueOnFailure

    def __str__(self):
        return serialize(self)
