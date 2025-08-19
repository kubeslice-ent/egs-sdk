import argparse
import os
import sys
from dataclasses import dataclass
from typing import List

import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
import egs
from egs.exceptions import ApiKeyInvalid, ApiKeyNotFound, WorkspaceAlreadyExists


@dataclass
class Workspace:
    name: str
    namespaces: List[str]
    username: str
    email: str
    clusters: List[str]
    apiKeyValidity: str


@dataclass
class WorkspaceConfig:
    projectname: str
    workspaces: List[Workspace]


def from_dict(data: dict) -> WorkspaceConfig:
    """Convert dictionary to WorkspaceConfig dataclass"""
    workspaces = [Workspace(**ws) for ws in data.get("workspaces", [])]
    return WorkspaceConfig(
        projectname=data.get("projectname", ""), workspaces=workspaces
    )


def readWorkspaceConfig(file: str) -> WorkspaceConfig:
    with open(file, "r") as f:
        config = yaml.safe_load(f)
        if not config or "workspaces" not in config:
            raise ValueError(
                "Configuration file is empty or missing 'workspaces' section."
            )
        return from_dict(config)


def get_env_variable(env_name: str) -> str:
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
                print(f"No apiKey found in {key_info}, skipping.")
                continue
            try:
                egs.delete_api_key(api_key=api_key_value, authenticated_session=auth)
                print(f"Deleted API key: {api_key_value}")
            except (ApiKeyInvalid, ApiKeyNotFound, ValueError) as err:
                print(f"Error deleting API key {api_key_value}: {err}")
            except Exception as err:
                print(f"Unexpected error while deleting API key {api_key_value}: {err}")

    except (ApiKeyInvalid, ApiKeyNotFound, ValueError) as err:
        print(f"Error listing API keys for {workspace_name}: {err}")
    except Exception as err:
        print(f"Unexpected error for {workspace_name}: {err}")


def delete_workspace(workspace_name, auth):
    """
    Deletes a workspace using the EGS API.
    """
    workspace_name = egs.delete_workspace(workspace_name, auth)
    print(f"Workspace Deleted: {workspace_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete Workspace Options")
    parser.add_argument("--config", required=True, help="Workspace configuration")

    args = parser.parse_args()

    try:
        # Check if either EGS_API_KEY or EGS_ACCESS_TOKEN is defined
        api_key = os.getenv("EGS_API_KEY")
        access_token = os.getenv("EGS_ACCESS_TOKEN")
        egs_endpoint = get_env_variable(env_name="EGS_ENDPOINT")

        if not api_key:
            if access_token:
                print(
                    "EGS_API_KEY not found. Creating Owner API Key using EGS_ACCESS_TOKEN..."
                )
                api_key = egs.create_owner_api_key(
                    egs_endpoint=egs_endpoint,
                    egs_token=access_token,
                    name="OwnerApiKey",
                    username="admin",
                )
            else:
                raise ValueError(
                    "Either EGS_API_KEY or EGS_ACCESS_TOKEN must be set in the environment."
                )

        print("Using API Key for authentication.")
        auth = egs.authenticate(egs_endpoint, api_key=api_key, sdk_default=False)

        if not args.config:
            raise ValueError(
                "Configuration file path must be provided using --config argument."
            )

        if not os.path.exists(args.config):
            raise FileNotFoundError(
                f"Missing the workspace configuration {args.config}"
            )

        workspace_config = readWorkspaceConfig(args.config)
        print(
            f"Loaded workspace configuration for project: {workspace_config.projectname}"
        )
        print(f"Found {len(workspace_config.workspaces)} workspaces to delete")

        for cur_ws in workspace_config.workspaces:

            try:
                api_keys_response = egs.list_api_keys(
                    workspace_name=cur_ws.name, authenticated_session=auth
                )
                # Extract the list of API key details from the response
                api_keys = api_keys_response.get("data", [])
                for key_info in api_keys:
                    api_key_value = key_info.get("apiKey")
                    if not api_key_value:
                        print(f"No apiKey found in {key_info}, skipping.")
                        continue
                    try:
                        response = egs.delete_api_key(
                            api_key=api_key_value, authenticated_session=auth
                        )
                        print(f"Deleted API key: {api_key_value}")
                    except (ApiKeyInvalid, ApiKeyNotFound, ValueError) as e:
                        print(f"Error deleting API key {api_key_value}: {e}")
                    except Exception as e:
                        print(
                            f"Unexpected error while deleting API key {api_key_value}: {e}"
                        )
            except (ApiKeyInvalid, ApiKeyNotFound, ValueError) as e:
                print(f"Error listing API key {cur_ws.name}: {e}")
            except Exception as e:
                print(f"Unexpected error for {cur_ws.name}: {e}")

            workspace_name = egs.delete_workspace(cur_ws.name, auth)
            print(f"Workspace Deleted: {workspace_name}")

    except EnvironmentError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ApiKeyInvalid as e:
        print("API Key is Invalid")
        print(e)
        sys.exit(1)
    except ApiKeyNotFound as e:
        print("API Key not found")
        print(e)
        sys.exit(1)
    except WorkspaceAlreadyExists as e:
        print("WorkspaceAlreadyExists")
        print(e)
        sys.exit(1)
    except Exception as e:
        print(e)
        print(f"Exception: {e}")
        sys.exit(1)
