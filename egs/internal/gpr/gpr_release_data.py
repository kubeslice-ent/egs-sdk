class GprReleaseRequest(object):
    def __init__(self, gpr_id: str):
        self.gprId = gpr_id
        self.earlyRelease = True

class GprReleaseResponse(object):
    def __init__(self, *args, **kwargs):
        pass