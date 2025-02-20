from typing import Optional

from egs.exceptions import UnhandledException
from egs.internal.client.egs_core_apis_client import new_egs_core_apis_client


def create_api_key(
        endpoint: str,
        access_token: str,
        name: str,
        role: str,
        valid_until: str,
        username: str = "admin",
        description: str = "",
        slice_name: Optional[str] = None
) -> str:
    auth = new_egs_core_apis_client(endpoint, access_token=access_token)
    req = {
        "name": name,
        "userName": username,
        "description": description,
        "role": role,
        "validUntil": valid_until,
    }
    if role in ["Editor", "Viewer"]:
        if not slice_name:
            raise ValueError("sliceName is required for roles Editor and Viewer")
        req["sliceName"] = slice_name

    api_response = auth.invoke_sdk_operation('/api/v1/token/create', 'POST', req)
    print(api_response)
    # if api_response.status_code == 409:
    #     raise APIKeyAlreadyExists(api_response)
    # elif api_response.status_code == 422:
    #     raise BadParameters(api_response)
    # elif api_response.status_code != 200:
    #     raise UnhandledException(api_response)
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return api_response.data["apiKey"]


def delete_api_key(
        endpoint: str,
        access_token: str,
        api_key: str,
):
    auth = new_egs_core_apis_client(endpoint, access_token=access_token)
    req = {"apiKey": api_key}
    api_response = auth.invoke_sdk_operation('/api/v1/token/delete', 'DELETE', req)
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return api_response.data


def list_api_keys(
        endpoint: str,
        access_token: str,
):
    auth = new_egs_core_apis_client(endpoint, access_token=access_token)
    api_response = auth.invoke_sdk_operation('/api/v1/token/list', 'GET')
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return api_response.data
