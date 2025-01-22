from egs.util.string_util import serialize

class UpdateGprNameRequest(object):
    def __init__(self, gpr_id: str, gpr_name: str):
        self.gprId = gpr_id
        self.gprName = gpr_name

    def __str__(self):
        return serialize(self)

class UpdateGprNameResponse(object):
    def __init__(self, *args, **kwargs):
        pass

    def __str__(self):
        return serialize(self)