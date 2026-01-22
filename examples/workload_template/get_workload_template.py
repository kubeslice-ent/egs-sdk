import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import egs

# Environment variables
EGS_API_ENDPOINT = os.environ.get("EGS_API_ENDPOINT")
EGS_API_KEY = os.environ.get("EGS_API_KEY")

# Configuration
TEMPLATE_NAME = "vllm-template"


def get_workload_template():
    """Example: Get a specific workload template by name."""

    if not EGS_API_ENDPOINT or not EGS_API_KEY:
        raise ValueError(
            "Please set EGS_API_ENDPOINT and EGS_API_KEY environment variables"
        )

    auth = egs.authenticate(
        endpoint=EGS_API_ENDPOINT,
        api_key=EGS_API_KEY,
    )

    try:
        template = egs.workloadTemplate.get(
            name=TEMPLATE_NAME,
            authenticated_session=auth,
        )
    except Exception as e:
        print(f"Error getting workload template: {e}")
        sys.exit(1)

    print(f"Workload Template: {template.name}")
    print(f"  Clusters: {template.clusterNames}")
    print(f"  Burst Duration: {template.burstDuration}")
    print(f"  Deletion Policy: {template.deletionPolicy}")
    print(f"  Service Account: {template.serviceAccount}")
    print(f"  Enable Burst: {template.enableBurst}")
    print(f"  Auto Placement: {template.autoPlacement}")
    print(f"  Created: {template.createdAt}")
    print(f"  Updated: {template.updatedAt}")
    print()

    # Helm configs
    print(f"Helm Configs ({len(template.helmConfigs)}):")
    for helm in template.helmConfigs:
        print(f"  - {helm.name}: {helm.chart} -> {helm.releaseNamespace}/{helm.releaseName}")

    # Manifest resources
    print(f"\nManifest Resources ({len(template.manifestResources)}):")
    for manifest in template.manifestResources:
        print(f"  - {manifest.name}: {manifest.manifest.get('kind', 'Unknown')}")

    # Steps
    print(f"\nSteps ({len(template.steps)}):")
    for i, step in enumerate(template.steps, 1):
        print(f"  {i}. {step.name} ({step.type})")


if __name__ == "__main__":
    get_workload_template()
