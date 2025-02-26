import json
from typing import Optional

import egs
from egs.authenticated_session import AuthenticatedSession
from egs.exceptions import UnhandledException
from egs.internal.client.egs_core_apis_client import new_egs_core_apis_client


def create_api_key(
        name: str,
        role: str,
        valid_until: str,
        username: str = "admin",
        description: str = "",
        slice_name: Optional[str] = None,
        authenticated_session: Optional[AuthenticatedSession] = None
) -> str:
    # Get authenticated session
    auth = egs.get_authenticated_session(authenticated_session)
    
    # Prepare request payload
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

    # Debug: Print payload to verify its structure
    print("Request Payload:", json.dumps(req, indent=4))

    # Make API request
    api_response = auth.client.invoke_sdk_operation('/api/v1/api-key', 'POST', req)

    # Debug: Print response details
    print("Full Response:", api_response)
    print("Status Code:", api_response.status_code)
    print("Raw Data:", api_response.data)

    # Check for success or handle errors
    if api_response.status_code != 200:
        raise UnhandledException(api_response)

    # Debug: Print parsed data
    try:
        print("Parsed JSON Response:", api_response.data)
        return api_response.data["apiKey"]
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
        print("Raw Response Data:", api_response.data)
        raise ValueError("The response is not a valid JSON.")
    except KeyError as e:
        print("Key Error:", e)
        print("Response Data:", api_response.data)
        raise ValueError("Expected key 'apiKey' not found in response data.")

# def create_api_key(
#         name: str,
#         role: str,
#         valid_until: str,
#         username: str = "admin",
#         description: str = "",
#         slice_name: Optional[str] = None,
#         authenticated_session: Optional[AuthenticatedSession] = None
# ) -> str:
#     auth = egs.get_authenticated_session(authenticated_session)
#     req = {
#         "name": name,
#         "userName": username,
#         "description": description,
#         "role": role,
#         "validUntil": valid_until,
#     }
#     if role in ["Editor", "Viewer"]:
#         if not slice_name:
#             raise ValueError("sliceName is required for roles Editor and Viewer")
#         req["sliceName"] = slice_name

#     api_response = auth.client.invoke_sdk_operation('/api/v1/api-key', 'POST', req)
#     print(api_response)
#     # if api_response.status_code == 409:
#     #     raise APIKeyAlreadyExists(api_response)
#     # elif api_response.status_code == 422:
#     #     raise BadParameters(api_response)
#     # elif api_response.status_code != 200:
#     #     raise UnhandledException(api_response)
#     if api_response.status_code != 200:
#         raise UnhandledException(api_response)
#     return api_response.data["apiKey"]


def delete_api_key(
        endpoint: str,
        access_token: str,
        api_key: str,
):
    auth = new_egs_core_apis_client(endpoint, access_token=access_token)
    req = {"apiKey": api_key}
    api_response = auth.invoke_sdk_operation('/api/v1/api-key',
                                             'DELETE',
                                             req)
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
