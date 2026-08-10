from typing import List

from egs.util.string_util import serialize


class CreateWorkspaceRequest(object):
    def __init__(
        self,
        workspace_name: str,
        clusters: List[str],
        namespaces: List[str],
        username: str,
        email: str,
    ):
        self.email = email
        self.username = username
        self.namespaces = namespaces
        self.clusters = clusters
        self.workspaceName = workspace_name

    def __str__(self):
        return serialize(self)


class CreateWorkspaceResponse(object):
    def __init__(self, workspaceName: str, *args, **kwargs):
        self.workspace_name = workspaceName

    def __str__(self):
        return serialize(self)

