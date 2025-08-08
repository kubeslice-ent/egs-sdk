import argparse
import os
import sys

import egs
from egs.internal.workspace.list_workspaces_data import ListWorkspacesResponse


def get_env_variable(env_name):
    """
    Fetches the value of an environment variable.
    Throws an error if the variable is not set.
    """
    value = os.getenv(env_name)
    if value is None:
        raise EnvironmentError(f"Environment variable '{env_name}' is not set.")
    return value


def workspace_and_cluster_exists(
    response: ListWorkspacesResponse, workspace_name: str, cluster_name: str
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


# Example usage
if __name__ == "__main__":
    # Set up command-line arguments
    parser = argparse.ArgumentParser(description="Make GPR Options")

    parser.add_argument("--request_name", required=True, help="Name of the GPU request")
    parser.add_argument("--cluster_name", required=True, help="Name of the Cluster")
    parser.add_argument(
        "--workspace_name", required=True, help="Name of workspace_name"
    )
    parser.add_argument(
        "--priority", required=True, type=int, help="The priority of the request."
    )
    parser.add_argument(
        "--exit_duration",
        required=True,
        help="The duration for which the GPU is requested for",
    )
    parser.add_argument("--gpu_shape", help="GPU Shape")
    parser.add_argument(
        "--idle_timeout_duration",
        help="Release the GPU if it has been idle for this duration",
    )
    parser.add_argument(
        "--enforce_idle_timeout", help="Enforce the idle timeout duration"
    )
    parser.add_argument("--enable_eviction", help="Enable eviction of the GPU")
    parser.add_argument("--requeue_on_failure", help="Requeue the request on failure")
    parser.add_argument("--enable_auto_gpu_selection", action="store_true", help="Enable auto GPU selection")
    parser.add_argument("--enable_auto_cluster_selection", action="store_true", help="Enable auto cluster selection")
    parser.add_argument("--prefered_cluster", nargs="+", help="List of preferred clusters")

    args = parser.parse_args()

    try:
        # Authenticate the EGS
        auth = egs.authenticate(
            get_env_variable("EGS_ENDPOINT"),
            get_env_variable("EGS_API_KEY"),
            sdk_default=False,
        )

        # print(auth)
        # Get the List of Workspaces
        workspaces = egs.list_workspaces(authenticated_session=auth)

        # Check If Workspace exist for the Cluster
        if workspace_and_cluster_exists(
            workspaces, args.workspace_name, args.cluster_name
        ):
            print(
                f"Workspace {args.workspace_name} exists in {args.cluster_name} cluster"
            )

            # Get the Inventory
            inventory = egs.workspace_inventory(
                args.workspace_name, authenticated_session=auth
            )
            cur_inventory = inventory.workspace_inventory[0]

            if args.gpu_shape:
                # Find matching workspace_inventory items
                matching_items = [
                    workspace
                    for workspace in inventory.workspace_inventory
                    if workspace.gpu_shape == args.gpu_shape
                ]
                if len(matching_items):
                    cur_inventory = matching_items[0]

            gpu_request_id = egs.request_gpu(
                request_name=args.request_name,
                workspace_name=args.workspace_name,
                cluster_name=args.cluster_name,
                node_count=1,
                gpu_per_node_count=cur_inventory.gpu_per_node,
                instance_type=cur_inventory.instance_type,
                memory_per_gpu=cur_inventory.memory_per_gpu,
                gpu_shape=cur_inventory.gpu_shape,
                exit_duration=args.exit_duration,
                priority=args.priority,
                idle_timeout_duration=args.idle_timeout_duration,
                enforce_idle_timeout=args.enforce_idle_timeout == "true",
                enable_eviction=args.enable_eviction == "true",
                requeue_on_failure=args.requeue_on_failure == "true",
                enable_auto_gpu_auto_selection=args.enable_auto_gpu_selection,
                enable_auto_cluster_selection=args.enable_auto_cluster_selection,
                prefered_cluster=args.prefered_cluster,
                authenticated_session=auth,
            )

            print("GPR Created Successfully with gpu_request_id: ", gpu_request_id)
        else:
            print(
                f"Workspace {args.workspace_name} doesnot exists in {args.cluster_name} cluster"
            )
            sys.exit(1)  # Exit with a non-zero status to indicate an error

    except EnvironmentError as e:
        print(f"Error: {e}")
        sys.exit(1)  # Exit with a non-zero status to indicate an error
    except Exception as e:
        print(e)
        print(f"Exception: {e}")
        sys.exit(1)
