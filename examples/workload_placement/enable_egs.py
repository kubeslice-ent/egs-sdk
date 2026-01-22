"""Example: Enable EGS on a workload placement."""

import os
import sys

import egs

# Environment variables
EGS_API_ENDPOINT = os.environ.get("EGS_API_ENDPOINT")
EGS_API_KEY = os.environ.get("EGS_API_KEY")

# Configuration
PLACEMENT_NAME = "vllm-workload-placement-sdk"


def enable_egs():
    """Enable EGS on a workload placement."""

    if not EGS_API_ENDPOINT or not EGS_API_KEY:
        raise ValueError(
            "Please set EGS_API_ENDPOINT and EGS_API_KEY environment variables"
        )

    auth = egs.authenticate(
        endpoint=EGS_API_ENDPOINT,
        api_key=EGS_API_KEY,
    )

    try:
        response = egs.workloadPlacement.enable_egs(
            name=PLACEMENT_NAME,
            authenticated_session=auth,
        )
    except Exception as e:
        print(f"Error enabling EGS: {e}")
        sys.exit(1)

    print(f"Enabled EGS on workload placement: {response.name}")


if __name__ == "__main__":
    enable_egs()
