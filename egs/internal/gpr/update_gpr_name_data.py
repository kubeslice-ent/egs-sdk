class UpdateGprNameRequest(object):
    def __init__(self, gpr_id: str, gpr_name: str):
        self.gprId = gpr_id
        self.gprName = gpr_name

class UpdateGprNameResponse(object):
    def __init__(self, *args, **kwargs):
        pass