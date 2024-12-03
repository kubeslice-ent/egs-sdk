import egs
from egs.authenticated_session import AuthenticatedSession
from egs.internal.client.egs_core_apis_client import new_egs_core_apis_client

def authenticate(
        endpoint: str,
        api_key: str,
        sdk_default: bool
) -> AuthenticatedSession:
    auth = new_egs_core_apis_client(endpoint, api_key)
    _ = auth.exchange_api_key_for_access_token()
    auth_session = AuthenticatedSession(auth, sdk_default)
    egs.update_global_session(auth_session)
    return auth_session