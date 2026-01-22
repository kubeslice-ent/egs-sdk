import os
import sys

import egs

# Environment variables
EGS_API_ENDPOINT = os.environ.get("EGS_API_ENDPOINT")
EGS_API_KEY = os.environ.get("EGS_API_KEY")

# Configuration
WORKSPACE_NAME = "pizza"


def list_by_workspace():
    """Example: List workload placements in a specific workspace."""

    if not EGS_API_ENDPOINT or not EGS_API_KEY:
        raise ValueError(
            "Please set EGS_API_ENDPOINT and EGS_API_KEY environment variables"
        )

    auth = egs.authenticate(
        endpoint=EGS_API_ENDPOINT,
        api_key=EGS_API_KEY,
    )

    try:
        response = egs.workloadPlacement.list_by_workspace(
            workspace_name=WORKSPACE_NAME,
            authenticated_session=auth,
        )
    except Exception as e:
        print(f"Error listing workload placements: {e}")
        sys.exit(1)

    print(f"Found {len(response.placements)} workload placement(s) in '{WORKSPACE_NAME}':\n")

    for wp in response.placements:
        print(f"  Name: {wp.name}")
        print(f"  Clusters: {wp.clusterNames}")
        print(f"  Status: {wp.status.placementStatus if wp.status else 'N/A'}")
        print(f"  Helm Configs: {len(wp.helmConfigs)}")
        print(f"  Manifest Resources: {len(wp.manifestResources)}")
        print()


if __name__ == "__main__":
    list_by_workspace()
