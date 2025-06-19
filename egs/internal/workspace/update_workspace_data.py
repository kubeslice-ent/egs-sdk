from egs.util.string_util import serialize

class UpdateWorkspaceRequest(object):
    def __init__(
            self,
            workspace_name: str,
            clusters: [str],
            namespaces: [str]):
        self.clusters = clusters
        self.namespaces = namespaces
        self.workspaceName = workspace_name

    def __str__(self):
        return serialize(self)

class UpdateWorkspaceResponse(object):
    def __init__(
            self,
            workspaceName: str,
            *args, **kwargs):
        self.workspace_name = workspaceName

    def __str__(self):
        return serialize(self)

class DetachClusterRequest(object):
    def __init__(
            self,
            workspace_name: str,
            cluster_name: str):
        self.workspaceName = workspace_name
        self.clusterName = cluster_name

    def __str__(self):
        return serialize(self)

class DetachClusterResponse(object):
    def __init__(
            self,
            workspaceName: str,
            detachedCluster: str,
            *args, **kwargs):
        self.workspace_name = workspaceName
        self.detached_cluster = detachedCluster

    def __str__(self):
        return serialize(self) 