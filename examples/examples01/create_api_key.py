import egs
from egs.exceptions import ApiKeyInvalid, ApiKeyNotFound

import argparse
import os
import yaml
import json



def get_env_variable(env_name):
    """
    Fetches the value of an environment variable.
    Throws an error if the variable is not set.
    """
    value = os.getenv(env_name)
    if value is None:
        raise EnvironmentError(f"Environment variable '{env_name}' is not set.")
    return value


if __name__ == "__main__":
    # Set up command-line arguments
    parser = argparse.ArgumentParser(description="Create API keys from a configuration file")
    parser.add_argument("--config", required=True, help="Path to API key configuration file")
    args = parser.parse_args()

    try:
        # Validate config file path
        if not os.path.exists(args.config):
            raise FileNotFoundError(f"Configuration file '{args.config}' not found.")

        # Load YAML config
        with open(args.config, "r", encoding="utf-8") as file:
            api_key_config = yaml.safe_load(file)
            if not api_key_config or "api_keys" not in api_key_config:
                raise ValueError("API Key configuration file is empty or missing 'api_keys' section.")
        print(f"🔍 api_key_config: {json.dumps(api_key_config, indent=2)}")

        # Fetch environment variables
        endpoint = get_env_variable("EGS_ENDPOINT")
        access_token = get_env_variable("EGS_ACCESS_TOKEN")

        # Loop through API key configs and create API keys
        for api_key_data in api_key_config["api_keys"]:

            try:
                name = api_key_data.get("name")
                username = api_key_data.get("userName", "admin")
                description = api_key_data.get("description", "")
                role = api_key_data.get("role")
                validity = api_key_data.get("apiKeyValidity")
                workspace_name = api_key_data.get("workspaceName", None)

                if not name or not role or not validity:
                    raise ValueError(f"Missing required fields in API key config: {api_key_data}")
                print(f"🔍 api_key_data: {json.dumps(api_key_data, indent=2)}")

                # Create API key
                response = egs.create_api_key(
                    endpoint=get_env_variable('EGS_ENDPOINT'),
                    access_token=get_env_variable('EGS_ACCESS_TOKEN'),
                    name=name,
                    role=role,
                    validity=validity,
                    username=username,
                    description=description,
                    workspace_name=workspace_name
                )

                print(f"✅ Successfully created API key: {name} api-key {response}")

            except (ApiKeyInvalid, ApiKeyNotFound, ValueError) as e:
                print(f"⚠️ Error creating API key '{name}': {e}")
            except Exception as e:
                print(f"❌ Unexpected error for '{name}': {e}")

    except Exception as e:
        print(f"❌ Fatal Error: {e}")
