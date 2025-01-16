from egs.util.string_util import serialize

class EgsApplicationException(Exception):
    def __init__(self, *args, **kwargs):
        self.args = args
        super().__init__(args, kwargs)
        pass

    def __str__(self):
        return serialize(self)

class ApiKeyExpired(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        pass

    def __str__(self):
        return serialize(self)

class ApiKeyInvalid(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        pass

    def __str__(self):
        return serialize(self)

class ApiKeyNotFound(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        pass

    def __str__(self):
        return serialize(self)

class GpuAlreadyProvisioned(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        pass

    def __str__(self):
        return serialize(self)

class GpuAlreadyReleased(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        pass

    def __str__(self):
        return serialize(self)

class ServerUnreachable(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        pass

    def __str__(self):
        return serialize(self)

class Unauthorized(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        pass

    def __str__(self):
        return serialize(self)

class WorkspaceAlreadyExists(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        pass

    def __str__(self):
        return serialize(self)

class BadParameters(Exception):
    def __init__(self, api_response, *args, **kwargs):
        self.api_response = api_response
        super().__init__(args, kwargs)
        pass

    def __str__(self):
        return serialize(self)

class UnhandledException(EgsApplicationException):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        pass

    def __str__(self):
        return serialize(self)