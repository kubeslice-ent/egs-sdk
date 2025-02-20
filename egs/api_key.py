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
    print(f"🔍 request: {req}")

    api_response = auth.invoke_sdk_operation('/api/v1/api-key/create', 'POST', req)
    # Debugging: Print raw response and Content-Type
    print(f"🔍 Raw response text: {api_response.text}")
    print(f"🔍 Response Content-Type: {api_response.headers.get('Content-Type')}")

    # Handle response based on Content-Type
    content_type = api_response.headers.get('Content-Type', '')
    if 'application/json' in content_type:
        try:
            response_data = api_response.json()
            print(f"✅ Parsed response JSON: {response_data}")
            return response_data["apiKey"]
        except ValueError as e:
            print(f"❌ JSON Decode Error: {e}")
            print("⚠️ Response might not be in JSON format.")
            raise UnhandledException("Failed to parse JSON response.")
    else:
        print("⚠️ Response is not in JSON format.")
        print(f"🔍 Raw response text: {api_response.text}")
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
    api_response = auth.invoke_sdk_operation('/api/v1/api-key/delete', 'DELETE', req)
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return api_response.data


def list_api_keys(
        endpoint: str,
        access_token: str,
):
    auth = new_egs_core_apis_client(endpoint, access_token=access_token)
    api_response = auth.invoke_sdk_operation('/api/v1/api-key/list', 'GET')
    if api_response.status_code != 200:
        raise UnhandledException(api_response)
    return api_response.data
