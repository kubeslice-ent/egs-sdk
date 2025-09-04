"""
Example script to list all workspace policies using the EGS SDK.

Usage Example:
python examples/workspace_policy/list_workspace_policies.py
"""

import argparse
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import egs
from egs.exceptions import UnhandledException


def get_env_variable(env_name):
    """
    Fetches the value of an environment variable.
    Throws an error if the variable is not set.
    """
    value = os.getenv(env_name)
    if value is None:
        raise EnvironmentError(f"Environment variable '{env_name}' is not set.")
    return value


# Example usage
if __name__ == "__main__":
    # Set up command-line arguments
    parser = argparse.ArgumentParser(description="List Workspace Policies")

    args = parser.parse_args()

    try:
        # Authenticate the EGS
        auth = egs.authenticate(
            get_env_variable("EGS_ENDPOINT"),
            get_env_variable("EGS_API_KEY"),
            sdk_default=False,
        )

        # List all workspace policies
        print("Listing all workspace policies...")
        response = egs.list_workspace_policies(authenticated_session=auth)

        print(f"\nFound {len(response.items)} workspace policies:")
        print("=" * 120)

        # Table header
        print(f"{'Workspace':<20} {'Priority':<10} {'Max GPRs':<10} {'Max Duration':<15} {'Requeue':<8} {'Auto Evict':<10} {'GPU Shapes':<20} {'Max GPU':<8} {'Max Memory':<10}")
        print("-" * 120)

        for policy in response.items:
            # Truncate long values
            workspace = policy.workspaceName[:18] + ".." if len(policy.workspaceName) > 20 else policy.workspaceName
            priority = policy.PriorityRange[:8] + ".." if len(policy.PriorityRange) > 10 else policy.PriorityRange
            max_duration = policy.maxExitDurationPerGPR[:13] + ".." if len(policy.maxExitDurationPerGPR) > 15 else policy.maxExitDurationPerGPR
            
            # Handle GPU constraints
            gpu_shapes = "N/A"
            max_gpu = "N/A"
            max_memory = "N/A"
            
            if policy.globalGPUConstraints:
                constraints = policy.globalGPUConstraints
                if constraints.gpuShapes:
                    gpu_shapes_str = ", ".join(constraints.gpuShapes)
                    gpu_shapes = gpu_shapes_str[:18] + ".." if len(gpu_shapes_str) > 20 else gpu_shapes_str
                max_gpu = str(constraints.maxGPUPerGpr)
                max_memory = f"{constraints.maxMemoryPerGpr}GB"

            print(f"{workspace:<20} {priority:<10} {policy.maxGPRs:<10} {max_duration:<15} {str(policy.requeueOnFailure):<8} {str(policy.enableAutoEviction):<10} {gpu_shapes:<20} {max_gpu:<8} {max_memory:<10}")

    except EnvironmentError as e:
        print(f"Error: {e}")
        sys.exit(1)  # Exit with a non-zero status to indicate an error
    except UnhandledException as e:
        print(f"Error listing workspace policies: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Exception: {e}")
        sys.exit(1)
