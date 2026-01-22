import os
import sys

import egs
from egs import (
    CreateWorkloadPlacementRequest,
    HelmConfig,
    ManifestResource,
    Step,
    StepType,
    YamlValues,
)

# Environment variables
EGS_API_ENDPOINT = os.environ.get("EGS_API_ENDPOINT")
EGS_API_KEY = os.environ.get("EGS_API_KEY")
HF_TOKEN = os.environ.get("HF_TOKEN")


def create_workload_placement():
    """Example: Create a workload placement with vLLM Helm chart."""

    if not EGS_API_ENDPOINT or not EGS_API_KEY:
        raise ValueError(
            "Please set EGS_API_ENDPOINT and EGS_API_KEY environment variables"
        )

    if not HF_TOKEN:
        raise ValueError("Please set HF_TOKEN environment variable")

    auth = egs.authenticate(
        endpoint=EGS_API_ENDPOINT,
        api_key=EGS_API_KEY,
    )

    # Helm values can be a YAML string or dict - passed directly to HelmConfig
    helm_values = f"""
routerSpec:
  enableRouter: false
  resources:
    limits:
      cpu: "4"
      memory: 32Gi
    requests:
      cpu: "2"
      memory: 8Gi
servingEngineSpec:
  modelSpec:
    - env:
        - name: VLLM_FLASHINFER_DISABLED
          value: "1"
      hf_token: {HF_TOKEN}
      modelURL: meta-llama/Llama-3.2-1B-Instruct
      name: llama3
      pvcStorage: 15Gi
      replicaCount: 1
      repository: vllm/vllm-openai
      requestCPU: 2
      requestGPU: 1
      requestMemory: 4Gi
      storageClass: linode-block-storage
      tag: v0.10.1
      vllmConfig:
        maxModelLen: 4096
"""

    manifest_yaml = """
apiVersion: v1
kind: PersistentVolume
metadata:
  name: vllm-1-pv
  labels:
    model: llama3-1-pv
spec:
  accessModes:
    - ReadWriteOnce
  capacity:
    storage: 100Gi
  hostPath:
    path: /data/llama3
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-path
"""

    helm_config = HelmConfig(
        name="vllm-app",
        chart="vllm/vllm-stack",
        releaseName="vllm",
        releaseNamespace="pizza",
        repoName="vllm",
        repoURL="https://vllm-project.github.io/production-stack",
        values=YamlValues(values=helm_values),  # YAML string is automatically parsed
    )

    # Manifest resource for PersistentVolume - parses YAML to dict
    e = YamlValues(values=manifest_yaml)
    print("basice ", e)
    pv_manifest = ManifestResource(
        name="vllm-1-pvc",
        manifest=e,
    )

    # Create the workload placement request
    request = CreateWorkloadPlacementRequest(
        workspaceName="pizza",
        name="vllm-workload-placement-sdk",
        clusterNames=["worker-1"],
        helmConfigs=[helm_config],
        manifestResources=[pv_manifest],
        steps=[
            Step(name="vllm-1-pvc", type=StepType.MANIFEST),
            Step(name="vllm-app", type=StepType.HELM),
        ],
    )

    # Create the workload placement
    try:
        data = egs.workloadPlacement.create(request, authenticated_session=auth)
    except Exception as e:
        print(f"Error creating workload placement: {e}")
        sys.exit(1)

    print(f"Created workload placement: {data.name}")


if __name__ == "__main__":
    create_workload_placement()
