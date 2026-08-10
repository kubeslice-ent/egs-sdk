"""
Script to list inventory and print GPU information.
"""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
import egs


def get_env_variable(env_name):
    """
    Fetches the value of an environment variable.
    Throws an error if the variable is not set.
    """
    value = os.getenv(env_name)
    if value is None:
        raise EnvironmentError(f"Environment variable '{env_name}' is not set.")
    return value


def print_inventory_table_header():
    """Print table header for inventory information"""
    print(f"{'='*120}")
    print(f"{'Node Name':<20} {'Cluster':<15} {'GPU Shape':<15} {'Instance Type':<20} {'Memory (GB)':<12} {'Total GPUs':<12} {'Available':<10} {'Status':<12}")
    print(f"{'='*120}")


def print_inventory_table_row(inventory_item):
    """Print a single row of inventory information in table format"""
    node_name = inventory_item.gpu_node_name[:17] + "..." if inventory_item.gpu_node_name and len(inventory_item.gpu_node_name) > 20 else (inventory_item.gpu_node_name or "N/A")
    cluster_name = inventory_item.cluster_name[:12] + "..." if inventory_item.cluster_name and len(inventory_item.cluster_name) > 15 else (inventory_item.cluster_name or "N/A")
    gpu_shape = inventory_item.gpu_shape[:12] + "..." if inventory_item.gpu_shape and len(inventory_item.gpu_shape) > 15 else (inventory_item.gpu_shape or "N/A")
    instance_type = inventory_item.instance_type[:17] + "..." if inventory_item.instance_type and len(inventory_item.instance_type) > 20 else (inventory_item.instance_type or "N/A")
    
    print(f"{node_name:<20} {cluster_name:<15} {gpu_shape:<15} {instance_type:<20} {inventory_item.memory or 0:<12} {inventory_item.gpu_count or 0:<12} {inventory_item.availableGPUs or 0:<10} {inventory_item.gpu_node_status or 'N/A':<12}")


def main():

    try:
        # Get environment variables
        endpoint = get_env_variable("EGS_ENDPOINT")
        api_key = get_env_variable("EGS_API_KEY")

        # Authenticate
        auth = egs.authenticate(endpoint, api_key)
        print(f"Authenticated successfully with endpoint: {endpoint}")

        # Get inventory
        print("Fetching inventory information...")
        inventory_response = egs.inventory(authenticated_session=auth)

        print(f"\n{'='*60}")
        print("INVENTORY SUMMARY")
        print(f"{'='*60}")

        total_managed = (
            len(inventory_response.managed_nodes)
            if inventory_response.managed_nodes
            else 0
        )
        total_unmanaged = (
            len(inventory_response.unmanaged_nodes)
            if inventory_response.unmanaged_nodes
            else 0
        )

        print(f"Total Managed Nodes: {total_managed}")
        print(f"Total Unmanaged Nodes: {total_unmanaged}")
        print(f"Total Nodes: {total_managed + total_unmanaged}")

        # Show managed nodes
        if inventory_response.managed_nodes:
            print(f"\nMANAGED NODES")
            print_inventory_table_header()
            for node in inventory_response.managed_nodes:
                print_inventory_table_row(node)
            print(f"{'='*120}")

        # Show unmanaged nodes
        if inventory_response.unmanaged_nodes:
            print(f"\nUNMANAGED NODES")
            print_inventory_table_header()
            for node in inventory_response.unmanaged_nodes:
                print_inventory_table_row(node)
            print(f"{'='*120}")

    except EnvironmentError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
