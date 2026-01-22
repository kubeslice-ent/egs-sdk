import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import egs
from egs.workload_template import (
    HelmConfig,
    ManifestResource,
    UpdateWorkloadTemplateRequest,
    YamlValues,
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

    # Updated helm values as YAML string
    updated_helm_values = """
routerSpec:
  enableRouter: false
servingEngineSpec:
  modelSpec:
    - name: llama3
      modelURL: meta-llama/Llama-3.2-1B-Instruct
      replicaCount: 2
      requestGPU: 1
"""

    # Updated helm config
    updated_helm_config = HelmConfig(
        name="vllm-app",
        chart="vllm/vllm-stack",
        releaseName="vllm",
        releaseNamespace="default",
        repoName="vllm",
        repoURL="https://vllm-project.github.io/production-stack",
        values=YamlValues(values=updated_helm_values),
    )

    # Updated manifest as YAML string
    updated_manifest_yaml = """
apiVersion: v1
kind: PersistentVolume
metadata:
  name: vllm-pv
  labels:
    app: vllm
    updated: "true"
spec:
  accessModes:
    - ReadWriteOnce
  capacity:
    storage: 20Gi
  hostPath:
    path: /data/vllm
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-path
"""

    # Updated manifest resource
    updated_manifest = ManifestResource(
        name="vllm-pvc",
        manifest=YamlValues(values=updated_manifest_yaml),
    )

    # Update request - include fields you want to update
    update_request = UpdateWorkloadTemplateRequest(
        burstDuration="2h",  # Changed from 1h to 2h
        clusterNames=["worker-1", "worker-2", "worker-3"],  # Added worker-3
        enableBurst=True,
        helmConfigs=[updated_helm_config],
        manifestResources=[updated_manifest],
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
