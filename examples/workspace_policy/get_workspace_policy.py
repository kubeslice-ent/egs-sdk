"""
Example script to get a specific workspace policy using the EGS SDK.

Usage Example:
python examples/workspace_policy/get_workspace_policy.py \
  --policy-name "my-workspace"
"""

import argparse
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import egs
from egs.exceptions import ResourceNotFound, UnhandledException


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
    parser = argparse.ArgumentParser(description="Get Workspace Policy")

    parser.add_argument(
        "--policy-name", required=True, help="Name of the workspace to get policy for"
    )

    args = parser.parse_args()

    try:
        auth = egs.authenticate(
            get_env_variable("EGS_ENDPOINT"),
            get_env_variable("EGS_API_KEY"),
            sdk_default=False,
        )

        # Get workspace policy
        print(f"Getting workspace policy for workspace: {args.policy_name}")
        response = egs.get_workspace_policy(
            policy_name=args.policy_name, authenticated_session=auth
        )

        policy = response.item
        print(f"\nWorkspace Policy Details:")
        print("=" * 50)
        print(f"Workspace: {policy.workspaceName}")
        print(f"Priority Range: {policy.PriorityRange}")
        print(f"Max GPRs: {policy.maxGPRs}")
        print(f"Max Exit Duration: {policy.maxExitDurationPerGPR}")
        print(f"Requeue on Failure: {policy.requeueOnFailure}")
        print(f"Enable Auto Eviction: {policy.enableAutoEviction}")

        if policy.globalGPUConstraints:
            constraints = policy.globalGPUConstraints
            print(f"\nGPU Constraints:")
            print(f"  GPU Shapes: {constraints.gpuShapes}")
            print(f"  Max GPU per GPR: {constraints.maxGPUPerGpr}")
            print(f"  Max Memory per GPR: {constraints.maxMemoryPerGpr} GB")
        else:
            print("\nNo GPU constraints configured")

    except EnvironmentError as e:
        print(f"Error: {e}")
        sys.exit(1)  # Exit with a non-zero status to indicate an error
    except ResourceNotFound as e:
        print(f"Workspace policy not found: {e}")
        print(
            f"Please check if the workspace '{args.policy_name}' exists and has a policy configured."
        )
        sys.exit(1)
    except UnhandledException as e:
        print(f"Error getting workspace policy: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Exception: {e}")
        sys.exit(1)
