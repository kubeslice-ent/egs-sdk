import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import egs

# Environment variables
EGS_API_ENDPOINT = os.environ.get("EGS_API_ENDPOINT")
EGS_API_KEY = os.environ.get("EGS_API_KEY")

# Configuration
WORKLOAD_PLACEMENT_NAME = "vllm-workload-placement-sdk"


def get_workload_placement():
    """Example: Get a specific workload placement by name."""

    if not EGS_API_ENDPOINT or not EGS_API_KEY:
        raise ValueError(
            "Please set EGS_API_ENDPOINT and EGS_API_KEY environment variables"
        )

    auth = egs.authenticate(
        endpoint=EGS_API_ENDPOINT,
        api_key=EGS_API_KEY,
    )

    try:
        wp = egs.workloadPlacement.get(
            name=WORKLOAD_PLACEMENT_NAME,
            authenticated_session=auth,
        )
    except Exception as e:
        print(f"Error getting workload placement: {e}")
        sys.exit(1)

    print(f"Workload Placement: {wp.name}")
    print(f"  Workspace: {wp.workspaceName}")
    print(f"  Clusters: {wp.clusterNames}")
    print(f"  Deletion Policy: {wp.deletionPolicy}")
    print(f"  Enable EGS: {wp.enableEGS}")
    print(f"  Enable Redistribute: {wp.enableRedistribute}")
    print(f"  Created: {wp.createdAt}")
    print(f"  Updated: {wp.updatedAt}")
    print()

    # Status details
    if wp.status:
        print(f"Status:")
        print(f"  Placement Status: {wp.status.placementStatus}")
        print(f"  Observed Clusters: {wp.status.observedClusterNames}")
        print()

        # Cluster placement decisions
        for decision in wp.status.clusterPlacementDecisions:
            print(f"  Cluster: {decision.clusterName}")
            print(f"    Phase: {decision.phase}")
            print(f"    Message: {decision.message}")
            print(f"    Current Step: {decision.currentStep}")
            print()

            # Step results
            for step in decision.stepResults:
                status = "✓" if step.success else "✗"
                print(f"    {status} Step '{step.name}' ({step.type}): {step.message}")

    # Helm configs
    print(f"\nHelm Configs ({len(wp.helmConfigs)}):")
    for helm in wp.helmConfigs:
        print(f"  - {helm.name}: {helm.chart} -> {helm.releaseNamespace}/{helm.releaseName}")

    # Manifest resources
    print(f"\nManifest Resources ({len(wp.manifestResources)}):")
    for manifest in wp.manifestResources:
        print(f"  - {manifest.name}: {manifest.manifest.get('kind', 'Unknown')}")

    # Steps
    print(f"\nSteps ({len(wp.steps)}):")
    for i, step in enumerate(wp.steps, 1):
        print(f"  {i}. {step.name} ({step.type})")


if __name__ == "__main__":
    get_workload_placement()
