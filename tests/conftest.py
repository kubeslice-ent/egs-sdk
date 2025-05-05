# tests/conftest.py
import os
import pytest
import egs
import uuid

@pytest.fixture(scope="session")
def auth_session():
    endpoint = os.getenv("EGS_ENDPOINT")
    api_key = os.getenv("EGS_API_KEY")
    if not endpoint or not api_key:
        pytest.skip("EGS_ENDPOINT and EGS_API_KEY must be set")
    return egs.authenticate(endpoint, api_key=api_key, sdk_default=False)

@pytest.fixture
def workspace(auth_session):
    # create a unique workspace for each test
    ws_name = f"test-ws-{uuid.uuid4().hex[:8]}"
    clusters = ["worker-1"]
    namespaces = [f"ns-{uuid.uuid4().hex[:6]}"]
    username = "testuser"
    email = f"{username}@example.com"
    ws = egs.create_workspace(ws_name, clusters, namespaces, username, email, authenticated_session=auth_session)
    yield ws, clusters, namespaces, username, email
    # teardown: delete the workspace
    try:
        egs.delete_workspace(ws, authenticated_session=auth_session)
    except Exception:
        pass 