import os
import egs
import argparse
import yaml
import sys

def get_env_variable(env_name):
    """
    Fetches the value of an environment variable.
    Throws an error if the variable is not set.
    """
    value = os.getenv(env_name)
    if value is None:
        raise EnvironmentError(f"Environment variable '{env_name}' is not set.")
    return value

def load_yaml_config(config_path):
    """
    Load and validate YAML configuration file.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
            if not config or "inference_endpoints" not in config:
                raise ValueError(
                    "Configuration file is empty or missing 'inference_endpoints' section."
                )
            return config
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML configuration file: {str(e)}") from e
    
if __name__ == "__main__":
    # Set up command-line arguments
    parser = argparse.ArgumentParser(
        description="Delete Endpoints from YAML configuration"
    )

    parser.add_argument(
        "--config",
        required=True,
        help="Path to YAML configuration file containing inference endpoint specifications"
    )

    args = parser.parse_args()

    # Delete inference endpoints from YAML configuration
    try:
        # Load and validate YAML configuration
        config = load_yaml_config(args.config)

        # Authenticate with EGS
        auth = egs.authenticate(
            get_env_variable('EGS_ENDPOINT'),
            get_env_variable('EGS_API_KEY'),
            sdk_default=False
        )

        # Get list of workspaces for validation
        workspaces = egs.list_workspaces(authenticated_session=auth)


        for endpoint_config in config.get("inference_endpoints", []):
            try:
                print(f"\n--- Processing endpoint: {endpoint_config.get('endpoint_name', 'unnamed')} ---")

                # Delete the inference endpoint
                inference_endpoint = egs.delete_inference_endpoint(
                    cluster_name=endpoint_config["cluster_name"],
                    endpoint_name=endpoint_config["endpoint_name"],
                    workspace_name=endpoint_config["workspace_name"],
                    authenticated_session=auth
                )

                print(f"✅ Endpoint deleted successfully: {inference_endpoint.endpoint_name}")

            except Exception as e:
                print(f"❌ Failed to delete endpoint '{endpoint_config.get('endpoint_name', 'unnamed')}': {e}")
                continue

    except FileNotFoundError as e:
        print(f"❌ Configuration file error: {e}")
        sys.exit(1)
    except EnvironmentError as e:
        print(f"❌ Environment error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)