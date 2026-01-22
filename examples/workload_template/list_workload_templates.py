import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import egs

# Environment variables
EGS_API_ENDPOINT = os.environ.get("EGS_API_ENDPOINT")
EGS_API_KEY = os.environ.get("EGS_API_KEY")


def list_workload_templates():
    """Example: List all workload templates."""

    if not EGS_API_ENDPOINT or not EGS_API_KEY:
        raise ValueError(
            "Please set EGS_API_ENDPOINT and EGS_API_KEY environment variables"
        )

    auth = egs.authenticate(
        endpoint=EGS_API_ENDPOINT,
        api_key=EGS_API_KEY,
    )

    try:
        response = egs.workloadTemplate.list(authenticated_session=auth)
    except Exception as e:
        print(f"Error listing workload templates: {e}")
        sys.exit(1)

    print(f"Found {len(response.templates)} workload template(s):\n")

    for template in response.templates:
        print(f"  Name: {template.name}")
        print(f"  Clusters: {template.clusterNames}")
        print(f"  Burst Duration: {template.burstDuration}")
        print(f"  Deletion Policy: {template.deletionPolicy}")
        print(f"  Helm Configs: {len(template.helmConfigs)}")
        print(f"  Manifest Resources: {len(template.manifestResources)}")
        print(f"  Created: {template.createdAt}")
        print()


if __name__ == "__main__":
    list_workload_templates()
