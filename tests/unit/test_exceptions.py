import pytest

from egs.exceptions import (
    ApiKeyExpired,
    ApiKeyInvalid,
    ApiKeyNotFound,
    BadParameters,
    EgsApplicationException,
    GpuAlreadyProvisioned,
    GpuAlreadyReleased,
    ServerUnreachable,
    Unauthorized,
    UnhandledException,
    WorkspaceAlreadyExists,
)
from egs.util.string_util import serialize


@pytest.mark.parametrize(
    "exc_cls,prefix",
    [
        (EgsApplicationException, "EgsApplicationException:"),
        (ApiKeyExpired, "ApiKeyExpiredException:"),
        (ApiKeyInvalid, "ApiKeyInvalidException:"),
        (ApiKeyNotFound, "ApiKeyNotFoundException:"),
        (GpuAlreadyProvisioned, "GpuAlreadyProvisionedException:"),
        (GpuAlreadyReleased, "GpuAlreadyReleasedException:"),
        (ServerUnreachable, "ServerUnreachableException:"),
        (Unauthorized, "UnauthorizedException:"),
        (WorkspaceAlreadyExists, "WorkspaceAlreadyExistsException:"),
        (BadParameters, "BadParametersException:"),
        (UnhandledException, "UnhandledException:"),
    ],
)
def test_exception_str_and_payload(exc_cls, prefix):
    exc = exc_cls({"reason": "test"})
    assert exc.exception == {"reason": "test"}
    text = str(exc)
    assert text.startswith(prefix)
    assert "reason" in text


def test_serialize_object_with_dict():
    class Sample:
        def __init__(self):
            self.name = "egs"
            self.value = 1

    assert serialize(Sample()) == '{"name": "egs", "value": 1}'


def test_serialize_primitive():
    assert serialize({"a": 1}) == '{"a": 1}'
