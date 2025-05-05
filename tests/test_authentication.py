# tests/test_authentication.py
import pytest
import egs
from egs.authenticated_session import AuthenticatedSession


def test_auth_success(auth_session):
    """Test that authentication succeeds with valid credentials"""
    assert isinstance(auth_session, AuthenticatedSession)
    assert hasattr(auth_session, 'client')
    assert auth_session.client is not None


def test_auth_invalid_endpoint():
    """Test that authentication fails with invalid endpoint"""
    with pytest.raises(Exception):
        egs.authenticate("http://invalid-endpoint:1234", api_key="fake-key", sdk_default=False) 