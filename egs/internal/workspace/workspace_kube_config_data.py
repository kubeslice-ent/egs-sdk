class GenerateWorkspaceKubeConfigRequest(object):
    def __init__(
            self,
            workspace_name: str):
        self.workspace_name = workspace_name

class GenerateWorkspaceKubeConfigResponse(object):
    def __init__(
            self,
            kubeConfig: str,
            *args, **kwargs):
        self.kube_config = kubeConfig