from egs.util.string_util import serialize

class ListWorkspacesRequest(object):
    def __init__(self):
        pass

    def __str__(self):
        return serialize(self)

class Namespace(object):
    def __init__(
            self,
            namespace: str,
            clusters: [str]):
        self.namespace = namespace
        self.clusters = clusters

    def __str__(self):
        return serialize(self)


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

    def __str__(self):
        return serialize(self)

class ListWorkspacesResponse(object):
    def __init__(self, workspaces: [Workspace]):
        ws = []
        for w in workspaces:
            ws.append(Workspace(**w))
        self.workspaces = ws

    def __str__(self):
        return serialize(self)
