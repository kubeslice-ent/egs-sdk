from egs.util.string_util import serialize

class ApiResponse(object):
    def __init__(self,
                 status: str,
                 message: str,
                 statusCode: int,
                 data: dict = None,
                 error: dict = None):
        self.error = error
        self.data = data
        self.status_code = statusCode
        self.message = message
        self.status = status

    def __str__(self):
        return serialize(self)