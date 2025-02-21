from typing import Optional

import egs
from egs.authenticated_session import AuthenticatedSession
from egs.internal.client.egs_core_apis_client import new_egs_core_apis_client


def authenticate(
        endpoint: str,
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
        sdk_default: bool = False
) -> AuthenticatedSession:
    """
    Authenticates using either an API key or an access token.
    It expects at least one of them to be present.

    :param endpoint: The EGS endpoint URL.
    :param api_key: The API key for authentication.
    :param access_token: The access token for authentication.
    :param sdk_default: If True, sets the authenticated session as the SDK default.
    :return: AuthenticatedSession object
    """
    # Ensure at least one of api_key or access_token is provided
    if not api_key and not access_token:
        raise ValueError("Either api_key or access_token must be provided.")

    # Use access_token if provided, otherwise exchange api_key for token
    if access_token:
        print("🔑 Using access token for authentication.")
        auth = new_egs_core_apis_client(endpoint, access_token=access_token)
    else:
        print("🔑 Using API key for authentication.")
        auth = new_egs_core_apis_client(endpoint, api_key=api_key)
        # Exchange API key for access token
        _ = auth.exchange_api_key_for_access_token()

    auth_session = AuthenticatedSession(auth, sdk_default)
    if sdk_default:
        egs.update_global_session(auth_session)
    return auth_session
