import os
import egs
import argparse
import json
import sys
from egs.internal.inference_endpoint.create_inference_endpoint_data import GpuSpec
from egs.internal.workspace.list_workspaces_data import ListWorkspacesResponse


# Example usage with raw model specification:
# python create_inference_endpoint_raw-spec.py \
#     --cluster_name "your-cluster" \
#     --workspace_name "your-workspace" \
#     --endpoint_name "llama2-endpoint" \
# --raw_model_spec '{"modelName": "huggingface", "storageURI": "meta-llama/meta-llama-3-8b-instruct", "args": ["--model_name=llama3", "--model_id=meta-llama/meta-llama-3-8b-instruct"], "secret": {"HF_TOKEN": {"valueFrom": {"secretKeyRef": {"name": "hf-secret", "key": "HF_TOKEN", "optional": false}}}}, "resources": {"cpu": "6", "memory": "24Gi"}}' \
#     --exit_duration "1h" \
#     --priority 100

# Optional GPU specification (if not provided, will use workspace inventory defaults):
#     --gpu_shape "A100" \
#     --instance_type "a2-highgpu-1g" \
#     --memory_per_gpu 40 \
#     --number_of_gpu_nodes 1 \
#     --number_of_gpus 1

# Note: raw_model_spec is a JSON string that directly defines the model specification
# It should contain fields like: modelName, storageURI, args, secret, resources

def get_env_variable(env_name):
    """
    Fetches the value of an environment variable.
    Throws an error if the variable is not set.
    """
    value = os.getenv(env_name)
    if value is None:
        raise EnvironmentError(f"Environment variable '{env_name}' is not set.")
    return value

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

#Example Usage
if __name__ == "__main__":
    # Set up command-line arguments
    parser = argparse.ArgumentParser(
                    description="Create Inference Endpoint with Raw Model Specification")
    # Required arguments
    parser.add_argument("--cluster_name", type=str, required=True, help="Name of the cluster")
    parser.add_argument("--workspace_name", type=str, required=True, help="Name of the workspace")
    parser.add_argument("--endpoint_name", type=str, required=True, help="Name of the endpoint")

    # Raw Model Spec argument (required for custom model specification)
    parser.add_argument("--raw_model_spec", type=str, required=True,
                       help="Raw model specification ")

    # GpuSpec arguments (optional - will use workspace inventory defaults if not provided)
    parser.add_argument("--gpu_shape", type=str, help="GPU shape (if not provided, will use inventory default)")
    parser.add_argument("--instance_type", type=str, help="Instance type (if not provided, will use inventory default)")
    parser.add_argument("--memory_per_gpu", type=int, help="Memory per GPU (if not provided, will use inventory default)")
    parser.add_argument("--number_of_gpu_nodes", type=int, help="Number of GPU nodes (if not provided, will use inventory default)")
    parser.add_argument("--number_of_gpus", type=int, help="Number of GPUs (if not provided, will use inventory default)")

    # Required GpuSpec arguments (no defaults available from inventory)
    parser.add_argument("--exit_duration", type=str, required=True, help="Exit duration (e.g., '1h', '30m')")
    parser.add_argument("--priority", type=int, required=True, help="Priority (integer value)")

    args = parser.parse_args()
    
    # Create inference endpoint
    try:
        # Authenticate the EGS
        auth = egs.authenticate(get_env_variable('EGS_ENDPOINT'),
                                get_env_variable('EGS_API_KEY'),
                                sdk_default=False)
        workspaces = egs.list_workspaces(authenticated_session=auth)
        if workspace_and_cluster_exists(workspaces,
                                        args.workspace_name,
                                        args.cluster_name):
            print(f'Workspace {args.workspace_name} exists in {args.cluster_name} cluster')

            # Get the Inventory
            inventory = egs.workspace_inventory(args.workspace_name,
                                                authenticated_session=auth)
            cur_inventory = inventory.workspace_inventory[0]

            if args.gpu_shape:
                # Find matching workspace_inventory items
                matching_items = [
                    workspace for workspace in inventory.workspace_inventory
                    if workspace.gpu_shape == args.gpu_shape
                ]
                if len(matching_items):
                    cur_inventory = matching_items[0]
                else:
                    raise ValueError(f"GPU shape {args.gpu_shape} not found in inventory")

            print(f"Creating Inference Endpoint using inventory {cur_inventory}")

            # Validate raw model spec JSON format
            try:
                raw_model_spec_dict = json.loads(args.raw_model_spec)
                print(f"Using raw model spec: {raw_model_spec_dict}")
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format for raw_model_spec: {e}")

            # Validate that we have the necessary GPU spec information
            instance_type = args.instance_type or cur_inventory.instance_type
            gpu_shape = args.gpu_shape or cur_inventory.gpu_shape
            memory_per_gpu = args.memory_per_gpu or cur_inventory.memory_per_gpu
            number_of_gpu_nodes = args.number_of_gpu_nodes or getattr(cur_inventory, 'number_of_gpu_nodes', 1)
            number_of_gpus = args.number_of_gpus or getattr(cur_inventory, 'number_of_gpus', 1)

            if not all([gpu_shape, instance_type, memory_per_gpu, number_of_gpu_nodes, number_of_gpus]):
                raise ValueError("Missing required GPU specification. Either provide GPU parameters via command line or ensure inventory has these values.")

            # Create the inference endpoint with custom model spec
            inference_endpoint = egs.create_inference_endpoint_with_custom_model_spec(
                cluster_name=args.cluster_name,
                endpoint_name=args.endpoint_name,
                workspace_name=args.workspace_name,
                raw_model_spec=args.raw_model_spec,
                gpu_spec=GpuSpec(
                    gpu_shape=gpu_shape,
                    instance_type=instance_type,
                    memory_per_gpu=memory_per_gpu,
                    number_of_gpu_nodes=number_of_gpu_nodes,
                    number_of_gpus=number_of_gpus,
                    exit_duration=args.exit_duration,
                    priority=args.priority
                ),
                authenticated_session=auth
            )
            print(f"Endpoint created successfully: {inference_endpoint.endpoint_name}")
        else:
            print(f'Workspace {args.workspace_name} does not exist in {args.cluster_name} cluster')
            sys.exit(1)  # Exit with a non-zero status to indicate an error

    except EnvironmentError as e:
        print(f"Environment Error: {e}")
        sys.exit(1)  # Exit with a non-zero status to indicate an error
    except ValueError as e:
        print(f"Value Error: {e}")
        sys.exit(1)  # Exit with a non-zero status to indicate an error
    except Exception as e:
        print(f"Unexpected Exception: {e}")
        sys.exit(1)  # Exit with a non-zero status to indicate an error
