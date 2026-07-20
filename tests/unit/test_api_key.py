import pytest

from egs.api_key import create_api_key, delete_api_key, list_api_keys
from egs.exceptions import UnhandledException
from tests.conftest import make_api_response


def test_create_api_key_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={"apiKey": "new-key"}
    )
    result = create_api_key(
        name="k1",
        role="Admin",
        validity="30d",
        authenticated_session=mock_session,
    )
    assert result == "new-key"
    path, method, req = mock_session.client.invoke_sdk_operation.call_args[0]
    assert path == "/api/v1/api-key"
    assert method == "POST"
    assert req["role"] == "Admin"
    assert "workspaceName" not in req


@pytest.mark.parametrize("role", ["Editor", "Viewer"])
def test_create_api_key_workspace_required(mock_session, role):
    with pytest.raises(ValueError, match="workspaceName is required"):
        create_api_key(
            name="k1",
            role=role,
            validity="30d",
            authenticated_session=mock_session,
        )


def test_create_api_key_with_workspace(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={"apiKey": "ws-key"}
    )
    result = create_api_key(
        name="k1",
        role="Editor",
        validity="7d",
        workspace_name="ws-1",
        authenticated_session=mock_session,
    )
    assert result == "ws-key"
    req = mock_session.client.invoke_sdk_operation.call_args[0][2]
    assert req["workspaceName"] == "ws-1"


def test_create_api_key_missing_key_in_response(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={}
    )
    with pytest.raises(ValueError, match="apiKey"):
        create_api_key(
            name="k1",
            role="Admin",
            validity="30d",
            authenticated_session=mock_session,
        )


@pytest.mark.parametrize(
    "code,msg",
    [
        (400, "Bad Request"),
        (401, "Unauthorized"),
        (403, "Forbidden"),
        (404, "Not Found"),
        (409, "Conflict"),
        (422, "Unprocessable"),
        (500, "Internal Server Error"),
        (503, "Service Unavailable"),
    ],
)
def test_create_api_key_mapped_errors(mock_session, code, msg):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=code
    )
    with pytest.raises(ValueError, match=msg):
        create_api_key(
            name="k1",
            role="Admin",
            validity="30d",
            authenticated_session=mock_session,
        )


def test_create_api_key_unhandled(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=418
    )
    with pytest.raises(UnhandledException):
        create_api_key(
            name="k1",
            role="Admin",
            validity="30d",
            authenticated_session=mock_session,
        )


def test_delete_api_key_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data="deleted"
    )
    assert delete_api_key("key", authenticated_session=mock_session) == "deleted"
    path, method, req = mock_session.client.invoke_sdk_operation.call_args[0]
    assert path == "/api/v1/api-key"
    assert method == "DELETE"
    assert req == {"apiKey": "key"}


@pytest.mark.parametrize("code", [401, 403, 404])
def test_delete_api_key_mapped_errors(mock_session, code):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=code
    )
    with pytest.raises(ValueError):
        delete_api_key("key", authenticated_session=mock_session)


def test_delete_api_key_unhandled(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=500
    )
    with pytest.raises(UnhandledException):
        delete_api_key("key", authenticated_session=mock_session)


def test_list_api_keys_success(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={"items": []}
    )
    result = list_api_keys(authenticated_session=mock_session)
    assert result == {"items": []}
    path, method = mock_session.client.invoke_sdk_operation.call_args[0][:2]
    assert path == "/api/v1/api-key/list"
    assert method == "GET"


def test_list_api_keys_with_workspace(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        data={"items": [{"name": "k"}]}
    )
    result = list_api_keys(workspace_name="ws-1", authenticated_session=mock_session)
    assert result["items"][0]["name"] == "k"
    path = mock_session.client.invoke_sdk_operation.call_args[0][0]
    assert path == "/api/v1/api-key/list?workspaceName=ws-1"


@pytest.mark.parametrize("code", [401, 403, 404])
def test_list_api_keys_mapped_errors(mock_session, code):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=code
    )
    with pytest.raises(ValueError):
        list_api_keys(authenticated_session=mock_session)


def test_list_api_keys_unhandled(mock_session):
    mock_session.client.invoke_sdk_operation.return_value = make_api_response(
        status_code=500
    )
    with pytest.raises(UnhandledException):
        list_api_keys(authenticated_session=mock_session)
