from egs.util.string_util import serialize

class EgsApplicationException(Exception):
    def __init__(self, value: any, *args, **kwargs):
        super().__init__(args, kwargs)
        self.exception = value
        pass

    def __str__(self):
        return f"EgsApplicationException: {serialize(self)}"

class ApiKeyExpired(Exception):
    def __init__(self, value: any, *args, **kwargs):
        super().__init__(args, kwargs)
        self.exception = value
        pass

    def __str__(self):
        return f"ApiKeyExpiredException: {serialize(self)}"

class ApiKeyInvalid(Exception):
    def __init__(self, value: any, *args, **kwargs):
        super().__init__(args, kwargs)
        self.exception = value
        pass

    def __str__(self):
        return f"ApiKeyInvalidException: {serialize(self)}"

class ApiKeyNotFound(Exception):
    def __init__(self, value: any, *args, **kwargs):
        super().__init__(args, kwargs)
        self.exception = value
        pass

    def __str__(self):
        return f"ApiKeyNotFoundException: {serialize(self)}"

class GpuAlreadyProvisioned(Exception):
    def __init__(self, value: any, *args, **kwargs):
        super().__init__(args, kwargs)
        self.exception = value
        pass

    def __str__(self):
        return f"GpuAlreadyProvisionedException: {serialize(self)}"

class GpuAlreadyReleased(Exception):
    def __init__(self, value: any, *args, **kwargs):
        super().__init__(args, kwargs)
        self.exception = value
        pass

    def __str__(self):
        return f"GpuAlreadyReleasedException: {serialize(self)}"

class ServerUnreachable(Exception):
    def __init__(self, value: any, *args, **kwargs):
        super().__init__(args, kwargs)
        self.exception = value
        pass

    def __str__(self):
        return f"ServerUnreachableException: {serialize(self)}"

class Unauthorized(Exception):
    def __init__(self, value: any, *args, **kwargs):
        super().__init__(args, kwargs)
        self.exception = value
        pass

    def __str__(self):
        return f"UnauthorizedException: {serialize(self)}"

class WorkspaceAlreadyExists(Exception):
    def __init__(self, value: any, *args, **kwargs):
        super().__init__(args, kwargs)
        self.exception = value
        pass

    def __str__(self):
        return f"WorkspaceAlreadyExistsException: {serialize(self)}"

class BadParameters(Exception):
    def __init__(self, value: any, *args, **kwargs):
        super().__init__(args, kwargs)
        self.exception = value
        pass

    def __str__(self):
        return f"BadParametersException: {serialize(self)}"

class UnhandledException(EgsApplicationException):
    def __init__(self, value: object, *args, **kwargs):
        super().__init__(value, args, kwargs)
        self.exception = value
        pass

    def __str__(self):
        return f"UnhandledException: {serialize(self)}"
