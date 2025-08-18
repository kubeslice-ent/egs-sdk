"""
Simple script to create GPR with both auto GPU and auto cluster selection enabled.
"""

import argparse
import os
import sys

# Add the project root to Python path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

import egs
from egs.gpu_requests import request_gpu_with_auto_selection


def main():
    parser = argparse.ArgumentParser(
        description="Create GPR with both auto GPU and auto cluster selection enabled"
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

        # Check if workspace exists
        print(f"Checking if workspace '{args.workspace_name}' exists...")
        workspaces = egs.list_workspaces(authenticated_session=auth)

        workspace_exists = False
        for workspace in workspaces.workspaces:
            if workspace.name == args.workspace_name:
                workspace_exists = True
                break

        if not workspace_exists:
            print(f"Error: Workspace '{args.workspace_name}' does not exist.")
            sys.exit(1)

        print(f"Workspace '{args.workspace_name}' exists")

        # Create GPR with both auto-selections enabled
        print(
            f"Creating GPR '{args.request_name}' with both auto-selections enabled..."
        )

        gpr_id = request_gpu_with_auto_selection(
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
            authenticated_session=auth,
        )

        print(f"GPR created successfully!")
        print(f"   GPR ID: {gpr_id}")
        print(f"   Request Name: {args.request_name}")

    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
