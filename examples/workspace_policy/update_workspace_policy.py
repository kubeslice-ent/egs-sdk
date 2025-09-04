"""
Example script to update a workspace policy using the EGS SDK.

Usage Example:
python examples/workspace_policy/update_workspace_policy.py \
  --policy-name "my-workspace" \
  --priority-range "high" \
  --max-gprs 5 \
  --gpu-shapes "NVIDIA-A10,Tesla-P100" \
  --max-gpu-per-gpr 2
"""

import argparse
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import egs
from egs.exceptions import BadParameters, ResourceNotFound, UnhandledException


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
    parser = argparse.ArgumentParser(description="Update Workspace Policy")

    parser.add_argument(
        "--policy-name",
        required=True,
        help="Name of the workspace to update policy for",
    )
    parser.add_argument(
        "--priority-range",
        choices=["high", "medium", "low"],
        help="Priority range for the workspace",
    )
    parser.add_argument("--max-gprs", type=int, help="Maximum number of GPRs allowed")
    parser.add_argument(
        "--max-exit-duration",
        help="Maximum exit duration per GPR (e.g., '1h', '30m', '1d')",
    )
    parser.add_argument(
        "--enforce-idle-timeout",
        action="store_true",
        help="Enable idle timeout enforcement",
    )
    parser.add_argument(
        "--requeue-on-failure", action="store_true", help="Enable requeue on failure"
    )
    parser.add_argument(
        "--enable-auto-eviction", action="store_true", help="Enable auto eviction"
    )
    parser.add_argument(
        "--gpu-shapes",
        help="Comma-separated list of allowed GPU shapes (e.g., 'NVIDIA-A10,Tesla-P100')",
    )
    parser.add_argument("--max-gpu-per-gpr", type=int, help="Maximum GPUs per GPR")
    parser.add_argument(
        "--max-memory-per-gpr", type=int, help="Maximum memory per GPR in GB"
    )

    args = parser.parse_args()

    try:
        # Authenticate the EGS
        auth = egs.authenticate(
            get_env_variable("EGS_ENDPOINT"),
            get_env_variable("EGS_API_KEY"),
            sdk_default=False,
        )

        # Prepare update parameters
        update_params = {}
        if args.priority_range is not None:
            update_params["priorityRange"] = args.priority_range
        if args.max_gprs is not None:
            update_params["maxGPRs"] = args.max_gprs
        if args.max_exit_duration is not None:
            update_params["maxExitDurationPerGPR"] = args.max_exit_duration
        if args.enforce_idle_timeout:
            update_params["enforceIdleTimeOut"] = True
        if args.requeue_on_failure:
            update_params["requeueOnFailure"] = True
        if args.enable_auto_eviction:
            update_params["enableAutoEviction"] = True
        if args.gpu_shapes is not None:
            gpu_shapes = [shape.strip() for shape in args.gpu_shapes.split(",")]
            update_params["gpuShapes"] = gpu_shapes
        if args.max_gpu_per_gpr is not None:
            update_params["maxGpuPerGpr"] = args.max_gpu_per_gpr
        if args.max_memory_per_gpr is not None:
            update_params["maxMemoryPerGpr"] = args.max_memory_per_gpr

        # Update workspace policy
        print(f"Updating workspace policy for workspace: {args.policy_name}")
        print(f"Updating parameters: {update_params}")

        response = egs.update_workspace_policy(
            policy_name=args.policy_name, **update_params, authenticated_session=auth
        )

        policy = response.item
        print(f"\nUpdated Workspace Policy:")
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

    except EnvironmentError as e:
        print(f"Error: {e}")
        sys.exit(1)  # Exit with a non-zero status to indicate an error
    except ResourceNotFound as e:
        print(f"Workspace policy not found: {e}")
        print(
            f"Please check if the workspace '{args.policy_name}' exists and has a policy configured."
        )
        sys.exit(1)
    except BadParameters as e:
        print(f"Invalid parameters provided: {e}")
        print("Please check your input parameters and try again.")
        sys.exit(1)
    except UnhandledException as e:
        print(f"Error updating workspace policy: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Exception: {e}")
        sys.exit(1)
