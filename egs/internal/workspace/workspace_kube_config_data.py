class GenerateWorkspaceKubeConfigRequest(object):
    def __init__(
            self,
            workspace_name: str):
        self.workspaceName = workspace_name

class GenerateWorkspaceKubeConfigResponse(object):
    def __init__(
            self,
            kubeConfig: str,
            *args, **kwargs):
        self.kube_config = kubeConfig