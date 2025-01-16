from egs.util.string_util import serialize

class UpdateGprPriorityRequest(object):
    def __init__(self, gpr_id: str, priority: int):
        self.gprId = gpr_id
        self.priority = priority

    def __str__(self):
        return serialize(self)

class UpdateGprPriorityResponse(object):
    def __init__(self, *args, **kwargs):
        pass

    def __str__(self):
        return serialize(self)