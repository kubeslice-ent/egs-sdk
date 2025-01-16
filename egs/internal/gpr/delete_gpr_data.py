from egs.util.string_util import serialize

class DeleteGprRequest(object):
    def __init__(self, gpr_id: str):
        self.gprId = gpr_id

    def __str__(self):
        return serialize(self)

class DeleteGprResponse(object):
    def __init__(self, *args, **kwargs):
        pass

    def __str__(self):
        return serialize(self)