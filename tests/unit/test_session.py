import pytest

import egs
from egs.authenticated_session import AuthenticatedSession
from egs.exceptions import Unauthorized
from egs.internal.client.api_reponse import ApiResponse


def test_update_and_get_global_session(mock_client):
    egs.update_global_session(None)
    assert egs.get_global_session() is None

    session = AuthenticatedSession(mock_client)
    egs.update_global_session(session)
    assert egs.get_global_session() is session
    egs.update_global_session(None)


def test_get_authenticated_session_prefers_explicit(mock_session):
    egs.update_global_session(None)
    assert egs.get_authenticated_session(mock_session) is mock_session


def test_get_authenticated_session_uses_global(mock_session):
    egs.update_global_session(mock_session)
    assert egs.get_authenticated_session(None) is mock_session
    egs.update_global_session(None)


def test_get_authenticated_session_raises_when_missing():
    egs.update_global_session(None)
    with pytest.raises(Unauthorized):
        egs.get_authenticated_session(None)


def test_authenticated_session_str(mock_client):
    session = AuthenticatedSession(mock_client, sdk_default=True)
    assert session.client is mock_client
    assert "client" in str(session)


def test_api_response_str():
    resp = ApiResponse(status="ok", message="m", statusCode=200, data={"a": 1})
    assert resp.status_code == 200
    assert resp.data == {"a": 1}
    assert "status" in str(resp)
