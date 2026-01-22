import os
import sys

import egs
from egs import (
    HelmConfig,
    ManifestResource,
    YamlValues,
)

# Environment variables
EGS_API_ENDPOINT = os.environ.get("EGS_API_ENDPOINT")
EGS_API_KEY = os.environ.get("EGS_API_KEY")

# Configuration
WORKLOAD_PLACEMENT_NAME = "vllm-workload-placement-sdk"


def update_workload_placement():
    """Example: Update a workload placement's helm configs or manifest resources."""

    if not EGS_API_ENDPOINT or not EGS_API_KEY:
        raise ValueError(
            "Please set EGS_API_ENDPOINT and EGS_API_KEY environment variables"
        )

    auth = egs.authenticate(
        endpoint=EGS_API_ENDPOINT,
        api_key=EGS_API_KEY,
    )

    # Updated helm config - must send complete config with new and existing values
    updated_helm_config = HelmConfig(
        name="vllm-app",
        chart="vllm/vllm-stack",
        releaseName="vllm",
        releaseNamespace="pizza",
        repoName="vllm",
        repoURL="https://vllm-project.github.io/production-stack",
        values={
            "routerSpec": {
                "enableRouter": True,  # Changed from False to True
            },
        },
    )

    # Updated manifest resource - must send complete resource as YAML or dict
    updated_manifest_yaml = """
apiVersion: v1
kind: PersistentVolume
metadata:
  name: vllm-1-pv
  labels:
    model: llama3-1-pv
    updated: "true"
spec:
  accessModes:
    - ReadWriteOnce
  capacity:
    storage: 20Gi
  hostPath:
    path: /data/llama3
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-path
"""

    updated_manifest = ManifestResource(
        name="vllm-1-pvc",
        manifest=YamlValues(values=updated_manifest_yaml),
    )

    try:
        response = egs.workloadPlacement.update(
            name=WORKLOAD_PLACEMENT_NAME,
            helm_configs=[updated_helm_config],
            manifest_resources=[updated_manifest],
            authenticated_session=auth,
        )
    except Exception as e:
        print(f"Error updating workload placement: {e}")
        sys.exit(1)

    print(f"Updated workload placement: {response.name}")


if __name__ == "__main__":
    update_workload_placement()
