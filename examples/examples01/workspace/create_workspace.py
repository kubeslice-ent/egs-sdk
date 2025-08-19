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


def get_env_variable(env_name):
    """
    Fetches the value of an environment variable.
    Throws an error if the variable is not set.
    """
    value = os.getenv(env_name)
    if value is None:
        raise EnvironmentError(f"Environment variable '{env_name}' is not set.")
    return value


def main():
    parser = argparse.ArgumentParser(description="Create Workspace Options")
    parser.add_argument("--config", required=True, help="Workspace configuration")
    args = parser.parse_args()

    try:
        # Check environment variables
        api_key = os.getenv("EGS_API_KEY")
        access_token = os.getenv("EGS_ACCESS_TOKEN")
        egs_endpoint = get_env_variable("EGS_ENDPOINT")

        # Handle API key creation if needed
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
                print("Owner API Key created successfully")
            else:
                raise ValueError(
                    "Either EGS_API_KEY or EGS_ACCESS_TOKEN must be set in the environment."
                )

        # Authenticate with EGS
        print("Authenticating with EGS...")
        auth = egs.authenticate(
            endpoint=egs_endpoint, api_key=api_key, sdk_default=False
        )
        print("Authentication successful")

        # Check if config file exists
        if not os.path.exists(args.config):
            raise FileNotFoundError(f"Configuration file not found: {args.config}")

        # Load and parse workspace configuration
        workspace_config = readWorkspaceConfig(args.config)
        print(
            f"Loaded workspace configuration for project: {workspace_config.projectname}"
        )
        print(f"Found {len(workspace_config.workspaces)} workspaces to create")

        for cur_ws in workspace_config.workspaces:
            print(f"Processing workspace: {cur_ws.name}")

            workspace_name = egs.create_workspace(
                cur_ws.name,
                cur_ws.clusters,
                cur_ws.namespaces,
                cur_ws.username,
                cur_ws.email,
                auth,
            )
            print(f"Workspace created successfully: {workspace_name}")

    except EnvironmentError as e:
        print(f"Error: {e}")
        sys.exit(1)  # Exit with a non-zero status to indicate an error
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


if __name__ == "__main__":
    main()
