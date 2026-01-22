import os
import sys

import egs

# Environment variables
EGS_API_ENDPOINT = os.environ.get("EGS_API_ENDPOINT")
EGS_API_KEY = os.environ.get("EGS_API_KEY")

# Configuration
WORKLOAD_PLACEMENT_NAME = "vllm-workload-placement-sdk"


def delete_workload_placement():
    """Example: Delete a workload placement."""

    if not EGS_API_ENDPOINT or not EGS_API_KEY:
        raise ValueError(
            "Please set EGS_API_ENDPOINT and EGS_API_KEY environment variables"
        )

    auth = egs.authenticate(
        endpoint=EGS_API_ENDPOINT,
        api_key=EGS_API_KEY,
    )

    # Confirm deletion
    print(f"About to delete workload placement: {WORKLOAD_PLACEMENT_NAME}")
    confirm = input("Are you sure? (yes/no): ")

    if confirm.lower() != "yes":
        print("Deletion cancelled.")
        sys.exit(0)

    try:
        response = egs.workloadPlacement.delete(
            name=WORKLOAD_PLACEMENT_NAME,
            authenticated_session=auth,
        )
    except Exception as e:
        print(f"Error deleting workload placement: {e}")
        sys.exit(1)

    print(f"Deleted workload placement: {response.name}")


if __name__ == "__main__":
    delete_workload_placement()
