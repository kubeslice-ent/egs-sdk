import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import egs
from egs.workload_template import (
    DeletionPolicy,
    HelmConfig,
    UpdateWorkloadTemplateRequest,
)

# Environment variables
EGS_API_ENDPOINT = os.environ.get("EGS_API_ENDPOINT")
EGS_API_KEY = os.environ.get("EGS_API_KEY")

# Configuration
TEMPLATE_NAME = "vllm-template"


def update_workload_template():
    """Example: Update a workload template."""

    if not EGS_API_ENDPOINT or not EGS_API_KEY:
        raise ValueError(
            "Please set EGS_API_ENDPOINT and EGS_API_KEY environment variables"
        )

    auth = egs.authenticate(
        endpoint=EGS_API_ENDPOINT,
        api_key=EGS_API_KEY,
    )

    # Update request - only include fields you want to update
    update_request = UpdateWorkloadTemplateRequest(
        burstDuration="2h",  # Changed from 1h to 2h
        clusterNames=["worker-1", "worker-2", "worker-3"],  # Added worker-3
        enableBurst=True,
    )

    try:
        response = egs.workloadTemplate.update(
            name=TEMPLATE_NAME,
            request=update_request,
            authenticated_session=auth,
        )
    except Exception as e:
        print(f"Error updating workload template: {e}")
        sys.exit(1)

    print(f"Updated workload template: {response.name}")


if __name__ == "__main__":
    update_workload_template()
