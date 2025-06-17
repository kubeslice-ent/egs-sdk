import os
import egs
import argparse
import json
import sys
import yaml
from egs.internal.inference_endpoint.create_inference_endpoint_data import GpuSpec
from egs.internal.workspace.list_workspaces_data import ListWorkspacesResponse


# Example usage:
# python create_inference_endpoint.py --config inference_config.yaml
#
# The YAML configuration file should contain inference endpoint specifications.
# See inference_config.yaml for an example configuration.

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

def validate_endpoint_config(endpoint_config):
    """
    Validate that an endpoint configuration has all required fields.
    """
    required_fields = [
        "endpoint_name", "cluster_name", "workspace_name",
        "raw_model_spec", "exit_duration", "priority"
    ]

    missing_fields = [field for field in required_fields if field not in endpoint_config]
    if missing_fields:
        raise ValueError(f"Missing required fields in endpoint configuration: {missing_fields}")

    return True

def workspace_and_cluster_exists(response: ListWorkspacesResponse,
                                 workspace_name: str,
                                 cluster_name: str) -> bool:
    """
    Check if a workspace with the given name exists and
    if the cluster name exists within its clusters.

    :param response: A ListWorkspacesResponse object.
    :param workspace_name: The name of the workspace to check for.
    :param cluster_name: The name of the cluster to check for within the workspace.
    :return: True if both the workspace and the cluster exist, False otherwise.
    """
    for workspace in response.workspaces:
        if workspace.name == workspace_name:
            if cluster_name in workspace.clusters:
                return True
            else:
                print(f"Workspace '{workspace_name}' exists, but cluster '{cluster_name}' does not.")
                return False
    print(f"Workspace '{workspace_name}' does not exist.")
    return False

# Example Usage
if __name__ == "__main__":
    # Set up command-line arguments
    parser = argparse.ArgumentParser(
        description="Create Inference Endpoints from YAML configuration"
    )

    parser.add_argument(
        "--config",
        required=True,
        help="Path to YAML configuration file containing inference endpoint specifications"
    )

    args = parser.parse_args()

    # Create inference endpoints from YAML configuration
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

                # Validate endpoint configuration
                validate_endpoint_config(endpoint_config)

                # Check if workspace and cluster exist
                if not workspace_and_cluster_exists(
                    workspaces,
                    endpoint_config["workspace_name"],
                    endpoint_config["cluster_name"]
                ):
                    print(f"Skipping endpoint '{endpoint_config['endpoint_name']}': "
                          f"Workspace '{endpoint_config['workspace_name']}' does not exist "
                          f"in cluster '{endpoint_config['cluster_name']}'")
                    continue

                # Get workspace inventory
                inventory = egs.workspace_inventory(
                    endpoint_config["workspace_name"],
                    authenticated_session=auth
                )
                cur_inventory = inventory.workspace_inventory[0]
                # print(cur_inventory)

                # Extract parameters from config
                instance_type = endpoint_config.get("instance_type")
                gpu_shape = endpoint_config.get("gpu_shape")
                requested_memory_per_gpu = endpoint_config.get("memory_per_gpu")
                requested_number_of_gpu_nodes = endpoint_config.get("number_of_gpu_nodes")
                requested_number_of_gpus = endpoint_config.get("number_of_gpus")

                matching_items = []

                # Match based on instance_type, optionally with gpu_shape
                if instance_type:
                    matching_items = [
                        item for item in inventory.workspace_inventory
                        if item.instance_type == instance_type and (not gpu_shape or item.gpu_shape == gpu_shape)
                    ]
                # Match only on gpu_shape if instance_type is not provided
                elif gpu_shape:
                    matching_items = [
                        item for item in inventory.workspace_inventory
                        if item.gpu_shape == gpu_shape
                    ]

                # Use matched inventory if found
                if matching_items:
                    cur_inventory = matching_items[0]
                elif instance_type or gpu_shape:
                    raise ValueError(
                        f"No matching inventory found for instance_type='{instance_type}'"
                        f"{' and gpu_shape=' + gpu_shape if gpu_shape else ''}"
                    )

                # Validate user-provided resource limits
                if requested_memory_per_gpu and requested_memory_per_gpu > cur_inventory.memory_per_gpu:
                    raise ValueError(
                        f"Requested memory_per_gpu ({requested_memory_per_gpu}) exceeds available "
                        f"({cur_inventory.memory_per_gpu})"
                    )

                if requested_number_of_gpu_nodes and requested_number_of_gpu_nodes > cur_inventory.gpu_per_node:
                    raise ValueError(
                        f"Requested number_of_gpu_nodes ({requested_number_of_gpu_nodes}) exceeds available "
                        f"({cur_inventory.gpu_per_node})"
                    )

                if requested_number_of_gpus and requested_number_of_gpus > cur_inventory.total_gpu_nodes:
                    raise ValueError(
                        f"Requested number_of_gpus ({requested_number_of_gpus}) exceeds available "
                        f"({cur_inventory.total_gpu_nodes})"
                    )

                # print(f"Using inventory: {cur_inventory}")
                

                # Determine GPU specifications (use config values or inventory defaults)
                gpu_shape = endpoint_config.get("gpu_shape") or cur_inventory.gpu_shape
                instance_type = endpoint_config.get("instance_type") or cur_inventory.instance_type
                memory_per_gpu = endpoint_config.get("memory_per_gpu") or cur_inventory.memory_per_gpu
                number_of_gpu_nodes = endpoint_config.get("number_of_gpu_nodes") or getattr(cur_inventory, 'number_of_gpu_nodes', 1)
                number_of_gpus = endpoint_config.get("number_of_gpus") or getattr(cur_inventory, 'number_of_gpus', 1)

                # Validate GPU specifications
                if not all([gpu_shape, instance_type, memory_per_gpu, number_of_gpu_nodes, number_of_gpus]):
                    raise ValueError("Missing required GPU specification. Provide GPU parameters in config or ensure inventory has these values.")
                
                # print(yaml.dump(endpoint_config['raw_model_spec'][0]))
                # raw_model_spec = yaml.dump(endpoint_config['raw_model_spec'][0], default_flow_style=False)
                # raw_model_spec_stringified = raw_model_spec.replace('\n', '\\n')
                # print(raw_model_spec_stringified)


                # Create the inference endpoint
                inference_endpoint = egs.create_inference_endpoint_with_custom_model_spec(
                    cluster_name=endpoint_config["cluster_name"],
                    endpoint_name=endpoint_config["endpoint_name"],
                    workspace_name=endpoint_config["workspace_name"],
                    raw_model_spec=yaml.dump(endpoint_config['raw_model_spec'][0]),
                    gpu_spec= None,
                    # GpuSpec(
                    #     gpu_shape=gpu_shape,
                    #     instance_type=instance_type,
                    #     memory_per_gpu=memory_per_gpu,
                    #     number_of_gpu_nodes=number_of_gpu_nodes,
                    #     number_of_gpus=number_of_gpus,
                    #     exit_duration=endpoint_config["exit_duration"],
                    #     priority=endpoint_config["priority"]
                    # ),
                    authenticated_session=auth
                )

                print(f"✅ Endpoint created successfully: {inference_endpoint.endpoint_name}")

            except Exception as e:
                print(f"❌ Failed to create endpoint '{endpoint_config.get('endpoint_name', 'unnamed')}': {e}")
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
