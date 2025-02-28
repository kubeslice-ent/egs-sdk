
import egs
from egs.internal.workspace.list_workspaces_data import ListWorkspacesResponse
from egs.exceptions import ApiKeyInvalid, ApiKeyNotFound, WorkspaceAlreadyExists


from kubernetes import client, config
import argparse
import os
import sys
import yaml
import time
import base64


def get_env_variable(env_name):
    """
    Fetches the value of an environment variable.
    Throws an error if the variable is not set.
    """
    value = os.getenv(env_name)
    if value is None:
        raise EnvironmentError(f"Environment variable '{env_name}' is not set.")
    return value


# Example usage
if __name__ == "__main__":
    # Set up command-line arguments
    parser = argparse.ArgumentParser(
                    description="Delete Workspace Options")

    parser.add_argument("--config",
                        required=True,
                        help="Workspace configuration")

    args = parser.parse_args()

    try:
        # Check if either EGS_API_KEY or EGS_ACCESS_TOKEN is defined
        api_key = os.getenv('EGS_API_KEY')
        access_token = os.getenv('EGS_ACCESS_TOKEN')

        # Authenticate the EGS
        if api_key:
            print("Using API Key for authentication.")
            auth = egs.authenticate(get_env_variable('EGS_ENDPOINT'),
                                    api_key=api_key,
                                    sdk_default=False)
        elif access_token:
            print("Using Access Token for authentication.")
            auth = egs.authenticate(get_env_variable('EGS_ENDPOINT'),
                                    access_token=access_token,
                                    sdk_default=False)
        else:
            raise ValueError("Either EGS_API_KEY or EGS_ACCESS_TOKEN must be set in the environment.")

        if not args.config:
            raise ValueError("Configuration file path must be provided using --config argument.")

        if not os.path.exists(args.config):
            raise FileNotFoundError(f"Missing the workspace configuration {args.config}")

        try:
            with open(args.config, "r", encoding="utf-8") as file:
                workspace_config = yaml.safe_load(file)
                if not workspace_config or 'workspaces' not in workspace_config:
                    raise ValueError("Workspace configuration file is empty or invalid.")
        except yaml.YAMLError as e:
            raise ValueError(f"Error loading workspace configuration file: {str(e)}")

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

            # # Retrieve and save the token
            # try:
            #     project_name = f'kubeslice-{workspace_config.get("projectname")}'
            #     token = get_kubeconfig_secret(workspace_name, project_name)
            #     token_path = os.path.join(workspace_dir, "token.txt")
            #     with open(token_path, "w", encoding="utf-8") as token_file:
            #         token_file.write(token)
            #     print(f"Token for {workspace_name} saved at {token_path}")
            # except Exception as e:
            #     print(f"Failed to retrieve and save token for {workspace_name}")
            #     raise ValueError(f"Failed to retrieve and save token for {workspace_name}: {str(e)}")

    except ApiKeyInvalid as e:
        # Do something when API key is not found
        print("API Key is Invalid")
        print(e)
    except ApiKeyNotFound as e:
        # Do something when API key is not found
        print("API Key not found")
        print(e)
    except WorkspaceAlreadyExists as e:
        # Do something when API key is not found
        print("WorkspaceAlreadyExists found")
        print(e)
    except Exception as e:
        print(e)
        print(f"Exception: {e}")
        # sys.exit(1)
