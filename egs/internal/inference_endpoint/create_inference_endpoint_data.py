from egs.util.string_util import serialize

class Resources(object):
    def __init__(
            self,
            cpu: str,
            memory: str
    ):
        self.cpu = cpu
        self.memory = memory

    def __str__(self):
        return serialize(self)


class ModelSpec(object):
    def __init__(
            self,
            model_name: str,
            storage_uri: str,
            args: [str],
            secret: dict,
            resources: Resources
    ):
        self.modelName = model_name
        self.storageURI = storage_uri
        self.args = args
        self.secret = secret
        self.resources = resources

    def __str__(self):
        return serialize(self)



class GpuSpec(object):
    def __init__(
            self,
            gpu_shape: str,
            instance_type: str,
            memory_per_gpu: int,
            number_of_gpu_nodes: int,
            number_of_gpus: int,
            exit_duration: str,
            priority: int
    ):
        self.gpuShape = gpu_shape
        self.instanceType = instance_type
        self.memoryPerGPU = memory_per_gpu
        self.numberOfGPUNodes = number_of_gpu_nodes
        self.numberOfGPUs = number_of_gpus
        self.exitDuration = exit_duration
        self.priority = priority

    def __str__(self):
        return serialize(self)



class CreateInferenceEndpointRequest(object):
    def __init__(
            self,
            cluster_name: str,
            endpoint_name: str,
            gpu_spec: GpuSpec,
            workspace: str,
            model_spec: ModelSpec,
            rawModelSpec: str
    ):
        self.clusterName = cluster_name
        self.endpointName = endpoint_name
        self.gpuSpec = gpu_spec
        self.workspace = workspace
        self.modelSpec = model_spec
        self.rawModelSpec = rawModelSpec

    def __str__(self):
        return serialize(self)


class CreateInferenceEndpointResponse(object):
    def __init__(self, endpointName: str, *args, **kwargs):
        self.endpoint_name = endpointName

    def __str__(self):
        return serialize(self)