import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import egs
from egs.workload_template import (
    CreateWorkloadTemplateRequest,
    DeletionPolicy,
    HelmConfig,
    Manifest,
    ManifestMetadata,
    ManifestResource,
    Step,
    StepType,
)

# Environment variables
EGS_API_ENDPOINT = os.environ.get("EGS_API_ENDPOINT")
EGS_API_KEY = os.environ.get("EGS_API_KEY")


def create_workload_template():
    """Example: Create a workload template with vLLM Helm chart."""

    if not EGS_API_ENDPOINT or not EGS_API_KEY:
        raise ValueError(
            "Please set EGS_API_ENDPOINT and EGS_API_KEY environment variables"
        )

    auth = egs.authenticate(
        endpoint=EGS_API_ENDPOINT,
        api_key=EGS_API_KEY,
    )

    # Helm config with YAML values
    helm_config = HelmConfig(
        name="vllm-app",
        chart="vllm/vllm-stack",
        releaseName="vllm",
        releaseNamespace="default",
        repoName="vllm",
        repoURL="https://vllm-project.github.io/production-stack",
        values={
            "routerSpec": {"enableRouter": False},
            "servingEngineSpec": {
                "modelSpec": [
                    {
                        "name": "llama3",
                        "modelURL": "meta-llama/Llama-3.2-1B-Instruct",
                        "replicaCount": 1,
                        "requestGPU": 1,
                    }
                ]
            },
        },
    )

    # Manifest resource for PersistentVolume
    pv_manifest = ManifestResource(
        name="vllm-pvc",
        manifest=Manifest(
            apiVersion="v1",
            kind="PersistentVolume",
            metadata=ManifestMetadata(
                name="vllm-pv",
                labels={"app": "vllm"},
            ),
            spec={
                "accessModes": ["ReadWriteOnce"],
                "capacity": {"storage": "15Gi"},
                "hostPath": {"path": "/data/vllm"},
                "persistentVolumeReclaimPolicy": "Retain",
                "storageClassName": "local-path",
            },
        ),
    )

    # Create the workload template request
    request = CreateWorkloadTemplateRequest(
        name="vllm-template",
        burstDuration="1h",
        deletionPolicy=DeletionPolicy.DELETE,
        clusterNames=["worker-1", "worker-2"],
        helmConfigs=[helm_config],
        manifestResources=[pv_manifest],
        steps=[
            Step(name="vllm-pvc", type=StepType.MANIFEST),
            Step(name="vllm-app", type=StepType.HELM),
        ],
        serviceAccount="default",
        enableBurst=True,
        autoPlacement=False,
    )

    try:
        response = egs.workloadTemplate.create(request, authenticated_session=auth)
    except Exception as e:
        print(f"Error creating workload template: {e}")
        sys.exit(1)

    print(f"Created workload template: {response.name}")


if __name__ == "__main__":
    create_workload_template()
