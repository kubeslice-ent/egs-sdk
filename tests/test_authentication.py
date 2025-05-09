# tests/test_authentication.py
import os
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


def test_auth_invalid_api_key():
    """Test that authentication fails with invalid API key"""
    endpoint = os.getenv("EGS_ENDPOINT")
    if not endpoint:
        pytest.skip("EGS_ENDPOINT must be set")
    with pytest.raises(Exception):
        egs.authenticate(endpoint, api_key="invalid-key", sdk_default=False)


def test_auth_empty_credentials():
    """Test that authentication fails with empty credentials"""
    with pytest.raises(ValueError):
        egs.authenticate("", api_key="", sdk_default=False)


def test_auth_malformed_endpoint():
    """Test that authentication fails with malformed endpoint URL"""
    with pytest.raises(Exception):
        egs.authenticate("not-a-valid-url", api_key="fake-key", sdk_default=False)


def test_auth_none_credentials():
    """Test that authentication fails with None credentials"""
    with pytest.raises(AttributeError):
        egs.authenticate(None, api_key=None, sdk_default=False) 