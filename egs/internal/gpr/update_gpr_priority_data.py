class UpdateGprPriorityRequest(object):
    def __init__(self, gpr_id: str, priority: int):
        self.gprId = gpr_id
        self.priority = priority

class UpdateGprPriorityResponse(object):
    def __init__(self, *args, **kwargs):
        pass