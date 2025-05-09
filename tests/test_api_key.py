# tests/test_api_key.py
import pytest
import uuid
import egs
from datetime import datetime, timedelta


def test_create_and_delete_owner_api_key(auth_session):
    """Test creating and deleting an Owner API key"""
    key_name = f"test-owner-{uuid.uuid4().hex[:6]}"
    # Use ISO date (YYYY-MM-DD) for Owner API key validity
    validity_date = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    api_key = egs.create_api_key(
        name=key_name,
        role="Owner",
        validity=validity_date,
        username="testuser",
        description="owner key",
        authenticated_session=auth_session
    )
    assert isinstance(api_key, str)

    # Delete the created API key
    resp = egs.delete_api_key(
        api_key=api_key,
        authenticated_session=auth_session
    )
    assert resp is not None


def test_create_editor_api_key(auth_session, workspace):
    """Test creating and deleting an Editor API key scoped to a workspace"""
    ws_name, clusters, namespaces, username, email = workspace
    key_name = f"test-editor-{uuid.uuid4().hex[:6]}"
    # Use ISO date (YYYY-MM-DD) for Editor API key validity
    validity_date = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    api_key = egs.create_api_key(
        name=key_name,
        role="Editor",
        validity=validity_date,
        username=username,
        description="editor key",
        workspace_name=ws_name,
        authenticated_session=auth_session
    )
    assert isinstance(api_key, str)

    # Delete the created API key
    resp = egs.delete_api_key(
        api_key=api_key,
        authenticated_session=auth_session
    )
    assert resp is not None


def test_create_api_key_missing_workspace(auth_session):
    """Test that creating an Editor key without workspace_name raises ValueError"""
    with pytest.raises(ValueError):
        egs.create_api_key(
            name="test",
            role="Editor",
            validity="1d",
            username="user",
            description="desc",
            authenticated_session=auth_session
        )


def test_list_api_keys(auth_session, workspace):
    """Test listing API keys for a workspace"""
    ws_name, clusters, namespaces, username, email = workspace
    resp = egs.list_api_keys(
        workspace_name=ws_name,
        authenticated_session=auth_session
    )
    assert isinstance(resp, dict)


def test_delete_api_key_not_found(auth_session):
    """Test deleting a non-existent API key raises ValueError"""
    with pytest.raises(ValueError):
        egs.delete_api_key(
            api_key="nonexistentkey",
            authenticated_session=auth_session
        )


def test_create_api_key_invalid_role(auth_session):
    """Test that creating an API key with invalid role raises ValueError"""
    with pytest.raises(ValueError):
        egs.create_api_key(
            name="test",
            role="InvalidRole",
            validity="1d",
            username="user",
            description="desc",
            authenticated_session=auth_session
        )


def test_create_api_key_expired_validity(auth_session):
    """Test that creating an API key with expired validity raises ValueError"""
    expired_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    with pytest.raises(ValueError):
        egs.create_api_key(
            name="test",
            role="Owner",
            validity=expired_date,
            username="user",
            description="desc",
            authenticated_session=auth_session
        )


def test_create_api_key_duplicate_name(auth_session):
    """Test that creating an API key with duplicate name returns a different key"""
    key_name = f"test-dup-{uuid.uuid4().hex[:6]}"
    validity_date = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Create first key
    first_key = egs.create_api_key(
        name=key_name,
        role="Owner",
        validity=validity_date,
        username="user",
        description="first key",
        authenticated_session=auth_session
    )
    assert isinstance(first_key, str)
    
    # Create second key with same name
    second_key = egs.create_api_key(
        name=key_name,
        role="Owner",
        validity=validity_date,
        username="user",
        description="second key",
        authenticated_session=auth_session
    )
    assert isinstance(second_key, str)
    
    # Verify that the keys are different
    assert first_key != second_key, "Duplicate API keys should return different values"
    
    # Clean up both keys
    egs.delete_api_key(api_key=first_key, authenticated_session=auth_session)
    egs.delete_api_key(api_key=second_key, authenticated_session=auth_session) 