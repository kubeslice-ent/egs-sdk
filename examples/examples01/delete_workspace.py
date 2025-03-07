import argparse
import os
import yaml
import json
import http.client
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
import egs
from egs.exceptions import ApiKeyInvalid, ApiKeyNotFound


def get_env_variable(env_name):
    """
    Fetches the value of an environment variable.
    Throws an error if the variable is not set.
    """
    value = os.getenv(env_name)
    if value is None:
        raise EnvironmentError(f"Environment variable '{env_name}' is not set.")
    return value


def delete_api_keys(workspace_name, auth):
    """
    Lists and deletes all API keys associated with the given workspace.
    """
    try:
        api_keys_response = egs.list_api_keys(
            workspace_name=workspace_name, authenticated_session=auth
        )
        api_keys = api_keys_response.get("data", [])

        for key_info in api_keys:
            api_key_value = key_info.get("apiKey")
            if not api_key_value:
                print(f"⚠️ No apiKey found in {key_info}, skipping.")
                continue
            try:
                egs.delete_api_key(api_key=api_key_value, authenticated_session=auth)
                print(f"✅ Deleted API key: {api_key_value}")
            except (ApiKeyInvalid, ApiKeyNotFound, ValueError) as err:
                print(f"⚠️ Error deleting API key {api_key_value}: {err}")
            except Exception as err:
                print(f"❌ Unexpected error while deleting API key {api_key_value}: {err}")

    except (ApiKeyInvalid, ApiKeyNotFound, ValueError) as err:
        print(f"⚠️ Error listing API keys for {workspace_name}: {err}")
    except Exception as err:
        print(f"❌ Unexpected error for {workspace_name}: {err}")


def delete_workspace(workspace_name, auth):
    """
    Deletes a workspace using the EGS API.
    """
    workspace_name = egs.delete_workspace(workspace_name, auth)
    print(f"✅ Workspace Deleted: {workspace_name}")


def create_owner_api_key():
    """
    Creates an Owner API Key using the EGS_ACCESS_TOKEN.
    """
    egs_endpoint = get_env_variable("EGS_ENDPOINT")
    egs_token = get_env_variable("EGS_ACCESS_TOKEN")

    # Parse the URL to extract host and path
    parsed_url = urlparse(egs_endpoint)
    host = parsed_url.netloc
    scheme = parsed_url.scheme
    path = "/api/v1/api-key"

    # Calculate validity (current date + 1 day) and format as "YYYY-MM-DD"
    validity = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")

    req_body = {
        "name": "OwnerAPIKey",
        "userName": "admin",
        "description": "OwnerAPIKey to delete workspaces",
        "role": "Owner",
        "validity": validity,
    }
    print(req_body)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {egs_token}",
    }

    # Use HTTP or HTTPS connection
    conn = http.client.HTTPSConnection(host) if scheme == "https" else http.client.HTTPConnection(host)

    try:
        conn.request("POST", path, body=json.dumps(req_body), headers=headers)
        resp = conn.getresponse()
        response_data = json.loads(resp.read().decode())

        if resp.status != 200:
            raise ValueError(f"❌ Failed to create Owner API Key: {resp.status} {response_data}")

        owner_api_key = response_data.get("data", {}).get("apiKey")

        if not owner_api_key:
            raise ValueError(f"❌ API key not found in response: {response_data}")

        print("✅ Successfully created Owner API Key.")
        return owner_api_key

    except Exception as err:
        raise RuntimeError(f"❌ Error creating API key: {err}") from err
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete Workspace Options")
    parser.add_argument("--config", required=True, help="Workspace configuration")

    args = parser.parse_args()

    try:
        # Check if either EGS_API_KEY or EGS_ACCESS_TOKEN is defined
        api_key = os.getenv("EGS_API_KEY")
        access_token = os.getenv("EGS_ACCESS_TOKEN")

        if not api_key:
            if access_token:
                print("🔑 EGS_API_KEY not found. Creating Owner API Key using EGS_ACCESS_TOKEN...")
                api_key = create_owner_api_key()
            else:
                raise ValueError(
                    "Either EGS_API_KEY or EGS_ACCESS_TOKEN must be set in the environment."
                )

        print("Using API Key for authentication.")
        auth = egs.authenticate(get_env_variable("EGS_ENDPOINT"),
                                api_key=api_key,
                                sdk_default=False)

        if not args.config:
            raise ValueError("Configuration file path must be provided using --config argument.")

        if not os.path.exists(args.config):
            raise FileNotFoundError(f"Missing the workspace configuration {args.config}")

        with open(args.config, "r", encoding="utf-8") as file:
            workspace_config = yaml.safe_load(file)

        if not workspace_config or "workspaces" not in workspace_config:
            raise ValueError("Workspace configuration file is empty or invalid.")


        for cur_ws in workspace_config.get('workspaces', []):

            try:
                api_keys_response = egs.list_api_keys(
                                            workspace_name=cur_ws['name'],
                                            authenticated_session=auth)
                # Extract the list of API key details from the response
                api_keys = api_keys_response.get('data', [])
                # Loop through and delete each API key by its 'apiKey' value
                for key_info in api_keys:
                    api_key_value = key_info.get('apiKey')
                    if not api_key_value:
                        print(f"⚠️ No apiKey found in {key_info}, skipping.")
                        continue
                    try:
                        response = egs.delete_api_key(
                            api_key=api_key_value,
                            authenticated_session=auth
                        )
                        print(f"✅ Deleted API key: {api_key_value}")
                    except (ApiKeyInvalid, ApiKeyNotFound, ValueError) as e:
                        print(f"⚠️ Error deleting API key {api_key_value}: {e}")
                    except Exception as e:
                        print(f"❌ Unexpected error while deleting API key {api_key_value}: {e}")
            except (ApiKeyInvalid, ApiKeyNotFound, ValueError) as e:
                print(f"⚠️ Error listing API key {cur_ws['name']}: {e}")
            except Exception as e:
                print(f"❌ Unexpected error for {cur_ws['name']}: {e}")

            workspace_name = egs.delete_workspace(
                cur_ws['name'],
                auth
            )
            print(f"Workspace Deleted: {workspace_name}")

    except ApiKeyInvalid as e:
        # Do something when API key is not found
        print("API Key is Invalid")
        print(e)
    except ApiKeyNotFound as e:
        # Do something when API key is not found
        print("API Key not found")
        print(e)
    except Exception as e:
        print(e)
        print(f"Exception: {e}")
        # sys.exit(1)

