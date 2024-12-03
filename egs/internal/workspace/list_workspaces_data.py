class ListWorkspacesRequest(object):
    def __init__(self):
        pass

class Namespace(object):
    def __init__(
            self,
            namespace: str,
            clusters: [str]):
        self.namespace = namespace
        self.clusters = clusters


class Workspace(object):
    def __init__(
            self,
            name: str,
            overlayNetworkDeploymentMode: str,
            maxClusters: int,
            sliceDescription: str,
            clusters: [str],
            namespaces: [Namespace],
            *args, **kwargs):
        self.name = name
        self.overlay_network_deployment_mode = overlayNetworkDeploymentMode
        self.max_clusters = maxClusters
        self.slice_description = sliceDescription
        self.clusters = clusters
        self.namespaces = namespaces

class ListWorkspacesResponse(object):
    def __init__(self, workspaces: [Workspace]):
        self.workspaces = workspaces