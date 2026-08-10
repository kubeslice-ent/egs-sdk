"""
Script to download kubeconfig and deploy GPU workload from YAML manifest.
"""

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from kubernetes import client, config

import egs
from egs.authenticated_session import AuthenticatedSession


@dataclass
class KubernetesClient:
    """Dataclass to hold Kubernetes client components"""

    api_client: client.ApiClient
    apps_v1_api: client.AppsV1Api
    core_v1_api: client.CoreV1Api


def get_env_variable(env_name):
    """
    Fetches the value of an environment variable.
    Throws an error if the variable is not set.
    """
    value = os.getenv(env_name)
    if value is None:
        raise EnvironmentError(f"Environment variable '{env_name}' is not set.")
    return value


def download_kubeconfig(
    workspace_name: str, cluster_name: str, auth: AuthenticatedSession, output_dir: str
):
    """
    Download kubeconfig file for a specific cluster in a workspace
    """
    try:
        workspace_dir = os.path.join(output_dir, workspace_name)
        os.makedirs(workspace_dir, exist_ok=True)

        print(
            f"Downloading kubeconfig for workspace: {workspace_name}, cluster: {cluster_name}"
        )
        print(f"Output directory: {workspace_dir}")

        # Get kubeconfig from EGS
        kubeconfig = egs.get_workspace_kubeconfig(
            workspace_name=workspace_name,
            cluster_name=cluster_name,
            authenticated_session=auth,
        )

        # Save kubeconfig to file
        kubeconfig_filename = f"{cluster_name}.yaml"
        kubeconfig_path = os.path.join(workspace_dir, kubeconfig_filename)

        with open(kubeconfig_path, "w", encoding="utf-8") as kube_file:
            kube_file.write(kubeconfig)

        print(
            f"Successfully downloaded kubeconfig for {cluster_name} to {kubeconfig_path}"
        )
        return kubeconfig_path

    except Exception as e:
        raise RuntimeError(
            f"Failed to download kubeconfig for workspace '{workspace_name}' and cluster '{cluster_name}': {e}"
        )


def initialize_kubernetes_client(kubeconfig_path: str) -> KubernetesClient:
    """Initialize Kubernetes client using the downloaded kubeconfig"""
    try:
        if kubeconfig_path and os.path.exists(kubeconfig_path):
            config.load_kube_config(config_file=kubeconfig_path)
            print(f"Loaded kubeconfig from: {kubeconfig_path}")
        else:
            raise FileNotFoundError(f"Kubeconfig file not found: {kubeconfig_path}")

        api_client = client.ApiClient()
        apps_v1_api = client.AppsV1Api(api_client)
        core_v1_api = client.CoreV1Api(api_client)
        print("Kubernetes client initialized successfully")

        return KubernetesClient(
            api_client=api_client, apps_v1_api=apps_v1_api, core_v1_api=core_v1_api
        )

    except Exception as e:
        print(f"Failed to initialize Kubernetes client: {e}")
        raise RuntimeError(f"Kubernetes client initialization failed: {e}")


def load_deployment_manifest(yaml_file_path: str):
    """Load deployment manifest from YAML file"""
    try:
        yaml_path = Path(yaml_file_path)

        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {yaml_file_path}")

        if not yaml_path.is_file():
            raise ValueError(f"Path is not a file: {yaml_file_path}")

        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                deployment_spec = yaml.safe_load(f)

            if not deployment_spec:
                raise ValueError("YAML file is empty or invalid")

            # Basic validation for deployment spec
            if deployment_spec.get("kind") != "Deployment":
                raise ValueError("YAML file must contain a Deployment resource")

            if not deployment_spec.get("metadata", {}).get("name"):
                raise ValueError("Deployment must have a name in metadata")

            print(f"Successfully loaded deployment manifest from: {yaml_file_path}")
            return deployment_spec

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}")
        except Exception as e:
            raise RuntimeError(f"Error reading YAML file: {e}")

    except Exception as e:
        print(f"Failed to load deployment manifest: {e}")
        raise


def create_gpr_for_deployment(
    auth, workspace_name: str, namespace: str, cluster_name: str
) -> str:
    """Create a GPR (GPU Request) for the deployment"""
    try:
        print(
            f"Creating GPR for workspace '{workspace_name}' in namespace '{namespace}' on cluster '{cluster_name}'"
        )

        # Create GPR with auto GPU selection but manual cluster selection
        gpr_id = egs.request_gpu_with_auto_gpu_selection(
            request_name=f"deployment-{namespace}",
            workspace_name=workspace_name,
            node_count=1,
            gpu_per_node_count=1,
            memory_per_gpu=22,  # 22GB memory per GPU
            exit_duration="1h",  # 1 hour duration
            priority=250,  # Higher priority
            idle_timeout_duration="30m",
            enforce_idle_timeout=True,
            requeue_on_failure=True,
            enable_eviction=True,
            preferred_clusters=[cluster_name],  # Manual cluster selection
            authenticated_session=auth,
        )

        print(f"GPR created successfully with ID: {gpr_id}")
        return gpr_id

    except Exception as e:
        raise RuntimeError(f"Failed to create GPR: {e}")


def create_deployment_from_manifest(
    k8s_client: KubernetesClient, deployment_spec: dict, namespace: str
):
    """Create deployment from loaded manifest"""
    try:
        deployment_name = deployment_spec["metadata"]["name"]
        print(
            f"Creating deployment '{deployment_name}' from manifest in namespace '{namespace}'"
        )

        deployment_spec["metadata"]["namespace"] = namespace

        # Ensure replicas is set to 1
        if "spec" not in deployment_spec:
            deployment_spec["spec"] = {}
        deployment_spec["spec"]["replicas"] = 1
        print("Deployment replicas set to 1")

        # Create deployment
        response = k8s_client.apps_v1_api.create_namespaced_deployment(
            body=deployment_spec, namespace=namespace
        )

        print(
            f"Deployment '{response.metadata.name}' created successfully in namespace '{namespace}'"
        )
        return response

    except client.ApiException as e:
        if e.status == 409:
            raise ValueError(f"Deployment already exists: {e.reason}")
        else:
            raise RuntimeError(f"Kubernetes API error: {e.status} - {e.reason}")
    except KeyError as e:
        raise ValueError(f"Invalid deployment manifest: missing required field {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to create deployment: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Download kubeconfig and deploy GPU workload from YAML manifest"
    )
    parser.add_argument("--workspace", required=True, help="Workspace name")
    parser.add_argument("--cluster", required=True, help="Cluster name")
    parser.add_argument(
        "--manifest", required=True, help="Path to deployment YAML manifest file"
    )
    parser.add_argument(
        "--namespace",
        required=True,
        help="Namespace for deployment (must be onboarded into the workspace)",
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.dirname(os.path.abspath(__file__)),
        help="Output directory for kubeconfig files (default: script directory)",
    )
    args = parser.parse_args()

    try:
        # Get environment variables
        api_key = get_env_variable("EGS_API_KEY")
        egs_endpoint = get_env_variable("EGS_ENDPOINT")

        # Authenticate with EGS
        print("Authenticating with EGS...")
        auth = egs.authenticate(
            endpoint=egs_endpoint, api_key=api_key, sdk_default=False
        )
        print("Authentication successful")

        print("\nStep 1: Downloading kubeconfig...")
        kubeconfig_path = download_kubeconfig(
            args.workspace, args.cluster, auth, args.output_dir
        )

        print("\nStep 2: Loading deployment manifest...")
        deployment_spec = load_deployment_manifest(args.manifest)

        print("\nStep 3: Initializing Kubernetes client...")
        k8s_client = initialize_kubernetes_client(kubeconfig_path)

        print("\nStep 4: Creating GPU Request (GPR)...")
        gpr_id = create_gpr_for_deployment(
            auth, args.workspace, args.namespace, args.cluster
        )

        print("\nStep 5: Creating deployment from manifest...")
        deployment = create_deployment_from_manifest(
            k8s_client, deployment_spec, args.namespace
        )

        print(f"GPR ID: {gpr_id}")
        print(f"Deployment: {deployment.metadata.name}")
        print(f"Namespace: {deployment.metadata.namespace}")
        print(f"Cluster: {args.cluster}")
        print(f"Kubeconfig: {kubeconfig_path}")
        print(f"Manifest: {args.manifest}")

    except EnvironmentError as e:
        print(f"Environment variable error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
