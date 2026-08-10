import http.client
import json
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlparse

import egs
from egs.authenticated_session import AuthenticatedSession
from egs.exceptions import UnhandledException


def create_owner_api_key(
    *,
    egs_endpoint: str,
    egs_token: str,
    name: str,
    username: str,
    validity: str = "",
    description: str = "",
):
    """
    Creates an Owner API Key using the EGS_ACCESS_TOKEN.
    """
    # Parse the URL to extract host and path
    parsed_url = urlparse(egs_endpoint)
    host = parsed_url.netloc
    scheme = parsed_url.scheme
    path = "/api/v1/api-key"

    # Calculate validity (current date + 1 day) and format as "YYYY-MM-DD"
    if not validity:
        validity = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")

    req_body = {
        "name": name,
        "userName": username,
        "description": description,
        "role": "Owner",
        "validity": validity,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {egs_token}",
    }

    # Use HTTP or HTTPS connection
    conn = (
        http.client.HTTPSConnection(host)
        if scheme == "https"
        else http.client.HTTPConnection(host)
    )

    try:
        conn.request("POST", path, body=json.dumps(req_body), headers=headers)
        res = conn.getresponse()
        response = json.loads(res.read().decode("utf-8"))
        if res.status != 200:
            raise ValueError(f"Failed to create Owner API Key: {res.status} {response}")

        owner_api_key = response.get("data", {}).get("apiKey")

        if not owner_api_key:
            raise ValueError(f"API key not found in response: {response}")
        return owner_api_key

    except Exception as err:
        raise RuntimeError(f"Error creating API key: {err}") from err
    finally:
        conn.close()


def create_api_key(
    name: str,
    role: str,
    validity: str,
    username: str = "admin",
    description: str = "",
    workspace_name: Optional[str] = None,
    authenticated_session: Optional[AuthenticatedSession] = None,
) -> str:
    """
    Create an API Key with the specified parameters.

    Args:
        name (str): Name of the API key.
        role (str): Role for the API key.
        validity (str): Validity period of the API key.
        username (str, optional): Username for the key. Defaults to 'admin'.
        description (str, optional): Description for the key.
        workspace_name (Optional[str], optional): Workspace name.
        authenticated_session (Optional[AuthenticatedSession], optional):
            Auth session.

    Returns:
        str: The created API Key.
    """
    auth = egs.get_authenticated_session(authenticated_session)

    req = {
        "name": name,
        "userName": username,
        "description": description,
        "role": role,
        "validity": validity,
    }

    if role in {"Editor", "Viewer"}:
        if not workspace_name:
            raise ValueError(
                "workspaceName is required for roles 'Editor' and 'Viewer'"
            )
        req["workspaceName"] = workspace_name

    api_response = auth.client.invoke_sdk_operation("/api/v1/api-key", "POST", req)

    if api_response.status_code == 200:
        try:
            return api_response.data["apiKey"]
        except (json.JSONDecodeError, KeyError) as exc:
            raise ValueError("Unexpected response: 'apiKey' missing.") from exc

    error_map = {
        400: "Bad Request: Invalid request format.",
        401: "Unauthorized: Invalid authentication.",
        403: "Forbidden: You lack required permissions.",
        404: "Not Found: Resource does not exist.",
        409: "Conflict: Resource already exists.",
        422: "Unprocessable Entity: Invalid request parameters.",
        500: "Internal Server Error: Server-side issue.",
        503: "Service Unavailable: Temporary server issue.",
    }

    if api_response.status_code in error_map:
        raise ValueError(error_map[api_response.status_code])

    raise UnhandledException(
        f"Unexpected status: {api_response.status_code}. "
        f"Response: {api_response.data}"
    )


def delete_api_key(
    api_key: str,
    authenticated_session: Optional[AuthenticatedSession] = None,
) -> str:
    """
    Delete an API Key by its value.

    Args:
        api_key (str): The API key to delete.
        authenticated_session (Optional[AuthenticatedSession], optional):
            Auth session.

    Returns:
        str: Confirmation of deletion.
    """
    auth = egs.get_authenticated_session(authenticated_session)
    req = {"apiKey": api_key}

    api_response = auth.client.invoke_sdk_operation("/api/v1/api-key", "DELETE", req)

    if api_response.status_code == 200:
        return api_response.data

    error_map = {
        401: "Unauthorized: Authentication failed.",
        403: "Forbidden: Insufficient permissions.",
        404: "API Key not found.",
    }

    if api_response.status_code in error_map:
        raise ValueError(error_map[api_response.status_code])

    raise UnhandledException(
        f"Unexpected status: {api_response.status_code}. "
        f"Response: {api_response.data}"
    )


def list_api_keys(
    workspace_name: Optional[str] = None,
    authenticated_session: Optional[AuthenticatedSession] = None,
) -> dict:
    """
    List API Keys, optionally filtered by workspace.

    Args:
        workspace_name (Optional[str], optional): Workspace to filter API keys.
        authenticated_session (Optional[AuthenticatedSession], optional):
            Auth session.

    Returns:
        dict: List of API keys.
    """
    auth = egs.get_authenticated_session(authenticated_session)

    path = "/api/v1/api-key/list"
    if workspace_name:
        path = f"{path}?workspaceName={workspace_name}"

    api_response = auth.client.invoke_sdk_operation(path, "GET")

    if api_response.status_code == 200:
        return api_response.data

    error_map = {
        401: "Unauthorized: Authentication failed.",
        403: "Forbidden: Insufficient permissions.",
        404: "No API Keys found.",
    }

    if api_response.status_code in error_map:
        raise ValueError(error_map[api_response.status_code])

    raise UnhandledException(
        f"Unexpected status: {api_response.status_code}. "
        f"Response: {api_response.data}"
    )
