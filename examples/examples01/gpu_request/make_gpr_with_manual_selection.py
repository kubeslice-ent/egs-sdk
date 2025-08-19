"""
Simple script to create GPR with both auto GPU and auto cluster selection disabled (manual selection).

Usage Example:
python examples/examples01/gpu_request/make_gpr_with_manual_selection.py \
  --request_name "color-gpr-001" \
  --workspace_name "color" \
  --priority 100 \
  --memory_per_gpu 22 \
  --exit_duration "1h" \
  --cluster_name "worker-1" \
  --instance_type "VM.GPU.A10.2" \
  --gpu_shape "NVIDIA-A10"
"""

import argparse
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
import egs
from egs.gpu_requests import request_gpu_with_manual_selection
from egs.internal.workspace.list_workspaces_data import ListWorkspacesResponse


def workspace_and_cluster_exists(
    response: ListWorkspacesResponse,
    workspace_name: str,
    cluster_name: str,
) -> bool:
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
                print(
                    f"Workspace '{workspace_name}' exists, but cluster '{cluster_name}' does not."
                )
                return False
    print(f"Workspace '{workspace_name}' does not exist.")
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Create GPR with both auto GPU and auto cluster selection disabled (manual selection)"
    )

    # Required arguments
    parser.add_argument("--request_name", required=True, help="Name of the GPU request")
    parser.add_argument("--workspace_name", required=True, help="Name of the workspace")
    parser.add_argument(
        "--priority",
        type=int,
        required=True,
        help="Priority of the request (lower number = higher priority)",
    )
    parser.add_argument(
        "--memory_per_gpu", type=int, required=True, help="Memory per GPU in GB"
    )
    parser.add_argument(
        "--exit_duration", required=True, help="Exit duration (e.g., '1h', '30m')"
    )
    parser.add_argument(
        "--cluster_name", required=True, help="Name of the specific cluster to use"
    )
    parser.add_argument(
        "--instance_type", required=True, help="Instance type (e.g., 'VM.GPU.A10.2')"
    )
    parser.add_argument(
        "--gpu_shape", required=True, help="GPU shape (e.g., 'NVIDIA-A10')"
    )

    # Optional arguments with defaults
    parser.add_argument(
        "--node_count", type=int, default=1, help="Number of nodes (default: 1)"
    )
    parser.add_argument(
        "--gpu_per_node_count",
        type=int,
        default=1,
        help="Number of GPUs per node (default: 1)",
    )
    parser.add_argument(
        "--idle_timeout_duration",
        default="30m",
        help="Idle timeout duration (default: '30m')",
    )
    parser.add_argument(
        "--enforce_idle_timeout",
        action="store_true",
        help="Enforce idle timeout (default: False)",
    )
    parser.add_argument(
        "--requeue_on_failure",
        action="store_true",
        help="Requeue on failure (default: False)",
    )
    parser.add_argument(
        "--enable_eviction",
        action="store_true",
        help="Enable eviction (default: False)",
    )

    args = parser.parse_args()

    try:
        # Authenticate using environment variables
        endpoint = os.getenv("EGS_ENDPOINT")
        api_key = os.getenv("EGS_API_KEY")

        if not endpoint or not api_key:
            print(
                "Error: EGS_ENDPOINT and EGS_API_KEY environment variables must be set"
            )
            sys.exit(1)

        # Authenticate
        auth = egs.authenticate(endpoint, api_key)
        print(f"Authenticated successfully with endpoint: {endpoint}")

        # Check if workspace and clusters exist
        print(f"Checking if workspace '{args.workspace_name}' exists...")
        workspaces = egs.list_workspaces(authenticated_session=auth)

        if not workspace_and_cluster_exists(
            workspaces, args.workspace_name, args.cluster_name
        ):
            print(f"Error: Workspace or clusters do not exist.")
            sys.exit(1)

        # Create GPR with both auto-selections disabled (manual selection)
        print(
            f"Creating GPR '{args.request_name}' with both auto-selections disabled (manual selection)..."
        )

        gpr_id = request_gpu_with_manual_selection(
            request_name=args.request_name,
            workspace_name=args.workspace_name,
            node_count=args.node_count,
            gpu_per_node_count=args.gpu_per_node_count,
            memory_per_gpu=args.memory_per_gpu,
            exit_duration=args.exit_duration,
            priority=args.priority,
            idle_timeout_duration=args.idle_timeout_duration,
            enforce_idle_timeout=args.enforce_idle_timeout,
            requeue_on_failure=args.requeue_on_failure,
            enable_eviction=args.enable_eviction,
            cluster_name=args.cluster_name,
            instance_type=args.instance_type,
            gpu_shape=args.gpu_shape,
            authenticated_session=auth,
        )

        print(f"GPR created successfully!")
        print(f"   GPR ID: {gpr_id}")
        print(f"   Request Name: {args.request_name}")
        print(f"   Cluster Name: {args.cluster_name}")
        print(f"   Instance Type: {args.instance_type}")
        print(f"   GPU Shape: {args.gpu_shape}")

    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
