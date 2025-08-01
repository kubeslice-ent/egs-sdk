from typing import List

from egs.util.string_util import serialize


class ListInferenceEndpointRequest(object):
    def __init__(self, workspace_name: str):
        self.workspace = workspace_name

    def __str__(self):
        return serialize(self)


class InferenceEndpointBrief(object):
    def __init__(
        self,
        endpointName: str,
        modelName: str,
        status: str,
        endpoint: str,
        clusterName: str,
        namespace: str,
        autoScalingStatus: str,
        *args,
        **kwargs
    ):
        self.endpoint_name = endpointName
        self.model_name = modelName
        self.status = status
        self.endpoint = endpoint
        self.cluster_name = clusterName
        self.namespace = namespace
        self.autoScalingStatus = autoScalingStatus

    def __str__(self):
        return serialize(self)


class ListInferenceEndpointResponse(object):
    def __init__(self, endpoints: List[dict], *args, **kwargs):
        ep: List[InferenceEndpointBrief] = []
        for e in endpoints:
            ep.append(InferenceEndpointBrief(**e))
        self.endpoints = ep

    def __str__(self):
        return serialize(self)
