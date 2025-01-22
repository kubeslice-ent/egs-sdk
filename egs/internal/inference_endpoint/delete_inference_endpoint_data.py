from egs.util.string_util import serialize

class DeleteInferenceEndpointRequest(object):
    def __init__(self,
                 endpoint_name: str,
                 workspace_name: str,
                 cluster_name: str):
        self.endpoint = endpoint_name
        self.workspace = workspace_name
        self.cluster = cluster_name

    def __str__(self):
        return serialize(self)

class DeleteInferenceEndpointResponse(object):
    def __init__(self, *args, **kwargs):
        pass

    def __str__(self):
        return serialize(self)
