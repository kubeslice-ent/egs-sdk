import json
from typing import Optional

import egs
from egs.authenticated_session import AuthenticatedSession
from egs.exceptions import UnhandledException, Unauthorized


def create_api_key(
    name: str,
    role: str,
    validity: str,
    username: str = "admin",
    description: str = "",
    workspace_name: Optional[str] = None,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> str:
    """
    Create an API Key with the specified parameters.

    Args:
        name (str): Name of the API key.
        role (str): Role for the API key.
        validity (str): Validity period of the API key.
        username (str): Username associated with the key. Defaults to 'admin'.
        description (str): Description for the API key.
        workspace_name (Optional[str]): Workspace name if applicable.
        authenticated_session (Optional[AuthenticatedSession]): Auth session.

    Returns:
        str: The created API Key.
    """
    # Get authenticated session
    auth = egs.get_authenticated_session(authenticated_session)

    # Prepare request payload
    req = {
        "name": name,
        "userName": username,
        "description": description,
        "role": role,
        "validity": validity,
    }
    if role in ["Editor", "Viewer"]:
        if not workspace_name:
            raise ValueError("workspaceName is required for roles Editor and Viewer")
        req["workspaceName"] = workspace_name

    # Make API request
    api_response = auth.client.invoke_sdk_operation(
        '/api/v1/api-key',
        'POST',
        req
    )

    # Handle HTTP Status Codes
    if api_response.status_code == 200:
        try:
            return api_response.data["apiKey"]
        except (json.JSONDecodeError, KeyError):
            raise ValueError("Unexpected response format: 'apiKey' not found.")
    if api_response.status_code == 400:
        raise ValueError("Bad Request: The server could not understand the request.")
    if api_response.status_code == 401:
        raise Unauthorized("Unauthorized: Authentication failed or access token is invalid.")
    if api_response.status_code == 403:
        raise PermissionError("Forbidden: You do not have permission to perform this action.")
    if api_response.status_code == 404:
        raise FileNotFoundError("Not Found: The requested resource does not exist.")
    if api_response.status_code == 409:
        raise ValueError("Conflict: The resource already exists.")
    if api_response.status_code == 422:
        raise ValueError("Unprocessable Entity: Invalid request parameters.")
    if api_response.status_code == 500:
        raise ConnectionError("Internal Server Error: An error occurred on the server.")
    if api_response.status_code == 503:
        raise ConnectionError("Service Unavailable: The server is temporarily unavailable.")

    raise UnhandledException(
        f"Unexpected status code: {api_response.status_code}. Response: {api_response.data}"
    )


def delete_api_key(
    api_key: str,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> str:
    """
    Delete an API Key by its value.

    Args:
        api_key (str): The API key to delete.
        authenticated_session (Optional[AuthenticatedSession]): Auth session.

    Returns:
        str: Confirmation of deletion.
    """
    # Get authenticated session
    auth = egs.get_authenticated_session(authenticated_session)
    req = {"apiKey": api_key}

    # Make API request
    api_response = auth.client.invoke_sdk_operation(
        '/api/v1/api-key',
        'DELETE',
        req
    )

    # Handle HTTP Status Codes
    if api_response.status_code == 200:
        return api_response.data
    if api_response.status_code == 404:
        raise FileNotFoundError("API Key not found.")
    if api_response.status_code == 401:
        raise Unauthorized("Unauthorized: Authentication failed.")
    if api_response.status_code == 403:
        raise PermissionError("Forbidden: You do not have permission.")

    raise UnhandledException(
        f"Unexpected status code: {api_response.status_code}. Response: {api_response.data}"
    )


def list_api_keys(
    workspace_name: Optional[str] = None,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> dict:
    """
    List API Keys, optionally filtered by workspace.

    Args:
        workspace_name (Optional[str]): Workspace to filter the keys.
        authenticated_session (Optional[AuthenticatedSession]): Auth session.

    Returns:
        dict: List of API keys.
    """
    # Get authenticated session
    auth = egs.get_authenticated_session(authenticated_session)

    # Construct URL path
    path = '/api/v1/api-key/list'
    if workspace_name:
        path = f"{path}?workspaceName={workspace_name}"

    # Make API request
    api_response = auth.client.invoke_sdk_operation(path, 'GET')

    # Handle HTTP Status Codes
    if api_response.status_code == 200:
        return api_response.data
    if api_response.status_code == 404:
        raise FileNotFoundError("No API Keys found.")
    if api_response.status_code == 401:
        raise Unauthorized("Unauthorized: Authentication failed.")
    if api_response.status_code == 403:
        raise PermissionError("Forbidden: You do not have permission.")

    raise UnhandledException(
        f"Unexpected status code: {api_response.status_code}. Response: {api_response.data}"
    )
