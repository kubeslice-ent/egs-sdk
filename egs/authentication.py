from typing import Optional

import egs
from egs.authenticated_session import AuthenticatedSession
from egs.internal.client.egs_core_apis_client import new_egs_core_apis_client


def authenticate(
        endpoint: str,
        api_key: str,
        sdk_default: bool = False
) -> AuthenticatedSession:
    """
    Authenticates using either an API key or an access token.
    It expects at least one of them to be present.

    :param endpoint: The EGS endpoint URL.
    :param api_key: The API key for authentication.
    :param sdk_default: If True, sets the authenticated session as the SDK default.
    :return: AuthenticatedSession object
    """
    auth = new_egs_core_apis_client(endpoint, api_key=api_key)
    # Exchange API key for access token
    _ = auth.exchange_api_key_for_access_token()

    auth_session = AuthenticatedSession(auth, sdk_default)
    if sdk_default:
        egs.update_global_session(auth_session)
    return auth_session
