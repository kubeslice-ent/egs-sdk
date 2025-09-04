from typing import Optional

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


class ResourceNotFound(Exception):
    def __init__(
        self,
        value: any,
        resource_type: str = "Resource",
        resource_id: Optional[str] = None,
        *args,
        **kwargs,
    ):
        super().__init__(args, kwargs)
        self.exception = value
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.status_code = getattr(value, "status_code", 404) if value else 404
        self.message = getattr(value, "message", None) if value else None
        pass

    def __str__(self):
        if self.resource_id:
            return f"ResourceNotFoundException: {self.resource_type} '{self.resource_id}' not found (HTTP {self.status_code})"
        else:
            return f"ResourceNotFoundException: {self.resource_type} not found (HTTP {self.status_code})"

    def __repr__(self):
        return f"ResourceNotFound(resource_type='{self.resource_type}', resource_id='{self.resource_id}', status_code={self.status_code})"


class UnhandledException(EgsApplicationException):
    def __init__(self, value: object, *args, **kwargs):
        super().__init__(value, args, kwargs)
        self.exception = value
        pass

    def __str__(self):
        return f"UnhandledException: {serialize(self)}"
