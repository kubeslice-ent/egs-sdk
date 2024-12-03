class CreateWorkspaceRequest(object):
    def __init__(
            self,
            workspace_name: str,
            clusters: [str],
            namespaces: [str],
            username: str,
            email: str):
        self.email = email
        self.username = username
        self.namespaces = namespaces
        self.clusters = clusters
        self.workspaceName = workspace_name

class CreateWorkspaceResponse(object):
    def __init__(
            self,
            workspaceName: str,
            *args, **kwargs):
        self.workspace_name = workspaceName