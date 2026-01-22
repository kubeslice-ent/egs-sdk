import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import egs

# Environment variables
EGS_API_ENDPOINT = os.environ.get("EGS_API_ENDPOINT")
EGS_API_KEY = os.environ.get("EGS_API_KEY")


def list_workload_placements():
    """Example: List all workload placements."""

    if not EGS_API_ENDPOINT or not EGS_API_KEY:
        raise ValueError(
            "Please set EGS_API_ENDPOINT and EGS_API_KEY environment variables"
        )

    auth = egs.authenticate(
        endpoint=EGS_API_ENDPOINT,
        api_key=EGS_API_KEY,
    )

    try:
        response = egs.workloadPlacement.list(authenticated_session=auth)
    except Exception as e:
        print(f"Error listing workload placements: {e}")
        sys.exit(1)

    print(f"Found {len(response.placements)} workload placement(s):\n")

    for wp in response.placements:
        print(f"  Name: {wp.name}")
        print(f"  Workspace: {wp.workspaceName}")
        print(f"  Clusters: {wp.clusterNames}")
        print(f"  Status: {wp.status.placementStatus if wp.status else 'N/A'}")
        print(f"  Created: {wp.createdAt}")
        print()


if __name__ == "__main__":
    list_workload_placements()
