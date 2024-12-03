class ApiKeyExpired(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        pass

class ApiKeyInvalid(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        pass

class ApiKeyNotFound(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        pass

class GpuAlreadyProvisioned(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        pass

class GpuAlreadyReleased(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        pass

class ServerUnreachable(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        pass

class Unauthorized(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        pass

class WorkspaceAlreadyExists(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        pass

class BadParameters(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        pass

class UnhandledException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        pass