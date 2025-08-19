"""
Script to list all GPU Requests (GPRs) for a workspace.

Usage Example:
python examples/examples01/gpu_request/list_gprs.py --workspace "color"
"""

import argparse
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
import egs
from egs.internal.gpr.gpr_status_data import GpuRequestData


def get_env_variable(env_name):
    """
    Fetches the value of an environment variable.
    Throws an error if the variable is not set.
    """
    value = os.getenv(env_name)
    if value is None:
        raise EnvironmentError(f"Environment variable '{env_name}' is not set.")
    return value


def print_gpr_table_header():
    """Print table header for GPR information"""
    print(f"{'='*120}")
    print(
        f"{'GPR Name':<20} {'GPR ID':<15} {'Cluster':<15} {'Status':<12} {'Total GPUs':<12} {'Instance Type':<15} {'GPU Shape':<15} {'Priority':<8}"
    )
    print(f"{'='*120}")


def print_gpr_table_row(gpr_data: GpuRequestData):
    """Print a single row of GPR information in table format"""
    gpr_name = (
        gpr_data.gpr_name[:17] + "..."
        if len(gpr_data.gpr_name) > 20
        else gpr_data.gpr_name
    )
    gpr_id = (
        gpr_data.gpr_id[:12] + "..." if len(gpr_data.gpr_id) > 15 else gpr_data.gpr_id
    )
    cluster_name = (
        gpr_data.cluster_name[:12] + "..."
        if len(gpr_data.cluster_name) > 15
        else gpr_data.cluster_name
    )
    status = (
        gpr_data.status.provisioning_status[:9] + "..."
        if len(gpr_data.status.provisioning_status) > 12
        else gpr_data.status.provisioning_status
    )
    instance_type = (
        gpr_data.instance_type[:12] + "..."
        if len(gpr_data.instance_type) > 15
        else gpr_data.instance_type
    )
    gpu_shape = (
        gpr_data.gpu_shape[:12] + "..."
        if len(gpr_data.gpu_shape) > 15
        else gpr_data.gpu_shape
    )

    # Calculate total GPUs
    total_gpus = gpr_data.number_of_gpus * gpr_data.number_of_gpu_nodes

    print(
        f"{gpr_name:<20} {gpr_id:<15} {cluster_name:<15} {status:<12} {total_gpus:<12} {instance_type:<15} {gpu_shape:<15} {gpr_data.priority:<8}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="List GPU Requests (GPRs) for a specific workspace"
    )
    parser.add_argument(
        "--workspace", required=True, help="Workspace name to fetch GPRs for"
    )
    args = parser.parse_args()

    try:
        # Get environment variables
        endpoint = get_env_variable("EGS_ENDPOINT")
        api_key = get_env_variable("EGS_API_KEY")

        # Authenticate
        print("Authenticating with EGS...")
        auth = egs.authenticate(endpoint, api_key)
        print("Authentication successful")

        # Fetch GPRs for the specified workspace
        print(f"Fetching GPRs for workspace: {args.workspace}")
        gpr_response = egs.gpu_request_status_for_workspace(
            workspace_name=args.workspace, authenticated_session=auth
        )

        if gpr_response.items:
            print(f"\nGPRs FOR WORKSPACE: {args.workspace.upper()}")
            print(f"Total GPRs: {len(gpr_response.items)}")

            print_gpr_table_header()
            for gpr in gpr_response.items:
                print_gpr_table_row(gpr)
            print(f"{'='*120}")
        else:
            print(f"No GPRs found in workspace: {args.workspace}")

    except EnvironmentError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
