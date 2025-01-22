from egs.util.string_util import serialize

class GenerateWorkspaceKubeConfigRequest(object):
    def __init__(
            self,
            workspace_name: str,
            cluster_name: str):
        self.workspaceName = workspace_name
        self.clusterName = cluster_name

    def __str__(self):
        return serialize(self)

class GenerateWorkspaceKubeConfigResponse(object):
    def __init__(
            self,
            kubeConfig: str,
            *args, **kwargs):
        self.kube_config = kubeConfig

    def __str__(self):
        return serialize(self)
