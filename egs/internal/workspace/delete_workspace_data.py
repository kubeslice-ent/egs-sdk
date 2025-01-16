from egs.util.string_util import serialize

class DeleteWorkspaceRequest(object):
    def __init__(self, workspace_name):
        self.workspaceName = workspace_name

    def __str__(self):
        return serialize(self)

class DeleteWorkspaceResponse(object):
    def __init__(self, *args, **kwargs):
        pass

    def __str__(self):
        return serialize(self)