from egs.util.string_util import serialize

class GprReleaseRequest(object):
    def __init__(self, gpr_id: str):
        self.gprId = gpr_id
        self.earlyRelease = True

    def __str__(self):
        return serialize(self)

class GprReleaseResponse(object):
    def __init__(self, *args, **kwargs):
        pass

    def __str__(self):
        return serialize(self)