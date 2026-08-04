import json
from unittest.mock import MagicMock, patch

import pytest

from egs.authentication import authenticate
from egs.exceptions import (
    ApiKeyExpired,
    ApiKeyInvalid,
    ApiKeyNotFound,
    ServerUnreachable,
    Unauthorized,
)
from egs.internal.client.egs_core_apis_client import (
    EgsCoreApisClient,
    new_egs_core_apis_client,
)


@pytest.mark.parametrize(
    "url,scheme,host,port,prefix",
    [
        ("http://example.com", "http", "example.com", 80, ""),
        ("https://example.com", "https", "example.com", 443, ""),
        ("https://example.com:8443", "https", "example.com", 8443, ""),
        ("http://example.com:8080/api", "http", "example.com", 8080, "/api"),
        ("https://example.com/v1/egs/", "https", "example.com", 443, "/v1/egs/"),
    ],
)
def test_client_url_parsing(url, scheme, host, port, prefix):
    client = EgsCoreApisClient(url, "key-1")
    assert client.scheme == scheme
    assert client.server_host == host
    assert client.server_port == port
    assert client.prefix == prefix
    assert client.api_key == "key-1"
    assert "api_key" in str(client)


def test_new_egs_core_apis_client():
    client = new_egs_core_apis_client("https://host.example", "k")
    assert isinstance(client, EgsCoreApisClient)
    assert client.server_host == "host.example"


def _mock_response(status, body):
    res = MagicMock()
    res.status = status
    res.read.return_value = json.dumps(body).encode("utf-8")
    return res


@patch("egs.internal.client.egs_core_apis_client.http.client.HTTPConnection")
def test_exchange_api_key_success_http(mock_http):
    conn = MagicMock()
    mock_http.return_value = conn
    conn.getresponse.return_value = _mock_response(
        200, {"data": {"token": "tok-123"}}
    )

    client = EgsCoreApisClient("http://api.local", "api-key")
    auth = client.exchange_api_key_for_access_token()
    assert auth.token == "tok-123"
    conn.request.assert_called_once()
    args = conn.request.call_args[0]
    assert args[0] == "POST"
    assert args[1] == "/api/v1/auth"


@patch("egs.internal.client.egs_core_apis_client.http.client.HTTPSConnection")
def test_exchange_api_key_success_https(mock_https):
    conn = MagicMock()
    mock_https.return_value = conn
    conn.getresponse.return_value = _mock_response(
        200, {"data": {"token": "secure-tok"}}
    )

    client = EgsCoreApisClient("https://api.local/prefix", "api-key")
    auth = client.exchange_api_key_for_access_token()
    assert auth.token == "secure-tok"
    args = conn.request.call_args[0]
    assert args[1] == "/prefix/api/v1/auth"


@patch("egs.internal.client.egs_core_apis_client.http.client.HTTPConnection")
def test_exchange_api_key_invalid(mock_http):
    conn = MagicMock()
    mock_http.return_value = conn
    conn.getresponse.return_value = _mock_response(400, {"message": "bad"})

    client = EgsCoreApisClient("http://api.local", "bad")
    with pytest.raises(ApiKeyInvalid):
        client.exchange_api_key_for_access_token()


@patch("egs.internal.client.egs_core_apis_client.http.client.HTTPConnection")
def test_exchange_api_key_expired(mock_http):
    conn = MagicMock()
    mock_http.return_value = conn
    conn.getresponse.return_value = _mock_response(
        401, {"message": "Api Key has expired"}
    )

    client = EgsCoreApisClient("http://api.local", "expired")
    with pytest.raises(ApiKeyExpired):
        client.exchange_api_key_for_access_token()


@patch("egs.internal.client.egs_core_apis_client.http.client.HTTPConnection")
def test_exchange_api_key_not_found(mock_http):
    conn = MagicMock()
    mock_http.return_value = conn
    conn.getresponse.return_value = _mock_response(
        401, {"message": "Api Key not found"}
    )

    client = EgsCoreApisClient("http://api.local", "missing")
    with pytest.raises(ApiKeyNotFound):
        client.exchange_api_key_for_access_token()


@patch("egs.internal.client.egs_core_apis_client.http.client.HTTPConnection")
def test_exchange_api_key_server_unreachable(mock_http):
    conn = MagicMock()
    mock_http.return_value = conn
    conn.getresponse.return_value = _mock_response(503, {"message": "down"})

    client = EgsCoreApisClient("http://api.local", "key")
    with pytest.raises(ServerUnreachable):
        client.exchange_api_key_for_access_token()


@patch.object(EgsCoreApisClient, "exchange_api_key_for_access_token")
@patch("egs.internal.client.egs_core_apis_client.http.client.HTTPConnection")
def test_invoke_sdk_operation_success(mock_http, mock_exchange):
    mock_exchange.return_value = MagicMock(token="tok")
    conn = MagicMock()
    mock_http.return_value = conn
    conn.getresponse.return_value = _mock_response(
        200,
        {
            "status": "success",
            "message": "ok",
            "statusCode": 200,
            "data": {"id": "1"},
        },
    )

    client = EgsCoreApisClient("http://api.local", "key")
    resp = client.invoke_sdk_operation("/api/v1/x", "POST", {"a": 1})
    assert resp.status_code == 200
    assert resp.data == {"id": "1"}
    headers = conn.request.call_args[0][3]
    assert headers["Authorization"] == "Bearer tok"
    assert headers["Content-Type"] == "application/json"


@patch.object(EgsCoreApisClient, "exchange_api_key_for_access_token")
@patch("egs.internal.client.egs_core_apis_client.http.client.HTTPSConnection")
def test_invoke_sdk_operation_get_no_body(mock_https, mock_exchange):
    mock_exchange.return_value = MagicMock(token="tok")
    conn = MagicMock()
    mock_https.return_value = conn
    conn.getresponse.return_value = _mock_response(
        200,
        {"status": "success", "message": "ok", "statusCode": 200, "data": {}},
    )

    client = EgsCoreApisClient("https://api.local", "key")
    resp = client.invoke_sdk_operation("/api/v1/x", "GET")
    assert resp.status_code == 200
    payload = conn.request.call_args[0][2]
    assert payload is None


@pytest.mark.parametrize("status", [401, 403])
@patch.object(EgsCoreApisClient, "exchange_api_key_for_access_token")
@patch("egs.internal.client.egs_core_apis_client.http.client.HTTPConnection")
def test_invoke_sdk_operation_unauthorized(mock_http, mock_exchange, status):
    mock_exchange.return_value = MagicMock(token="tok")
    conn = MagicMock()
    mock_http.return_value = conn
    conn.getresponse.return_value = _mock_response(
        status, {"status": "error", "message": "no", "statusCode": status}
    )

    client = EgsCoreApisClient("http://api.local", "key")
    with pytest.raises(Unauthorized):
        client.invoke_sdk_operation("/api/v1/x", "GET")


@patch("egs.authentication.new_egs_core_apis_client")
def test_authenticate_without_sdk_default(mock_new_client):
    client = MagicMock()
    mock_new_client.return_value = client
    client.exchange_api_key_for_access_token.return_value = MagicMock(token="t")

    session = authenticate("https://api.local", "key", sdk_default=False)
    assert session.client is client
    client.exchange_api_key_for_access_token.assert_called_once()


@patch("egs.authentication.new_egs_core_apis_client")
def test_authenticate_with_sdk_default(mock_new_client):
    import egs

    client = MagicMock()
    mock_new_client.return_value = client
    client.exchange_api_key_for_access_token.return_value = MagicMock(token="t")

    egs.update_global_session(None)
    session = authenticate("https://api.local", "key", sdk_default=True)
    assert egs.get_global_session() is session
    egs.update_global_session(None)
