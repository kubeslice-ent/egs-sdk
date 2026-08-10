import argparse
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
import egs
from egs.authenticated_session import AuthenticatedSession


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

    except Exception as e:
        raise RuntimeError(
            f"Failed to download kubeconfig for workspace '{workspace_name}' and cluster '{cluster_name}': {e}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Download Kubeconfig File for a Specific Cluster"
    )
    parser.add_argument("--workspace", required=True, help="Workspace name")
    parser.add_argument("--cluster", required=True, help="Cluster name")
    parser.add_argument(
        "--output-dir",
        default=os.path.dirname(os.path.abspath(__file__)),
        help="Output directory for kubeconfig files (default: script directory)",
    )
    args = parser.parse_args()

    try:
        # api key should have necessary permissions
        api_key = get_env_variable("EGS_API_KEY")
        egs_endpoint = get_env_variable("EGS_ENDPOINT")

        # Authenticate with EGS
        print("Authenticating with EGS...")
        auth = egs.authenticate(
            endpoint=egs_endpoint, api_key=api_key, sdk_default=False
        )
        print("Authentication successful")

        # Download kubeconfig for the specified workspace and cluster
        download_kubeconfig(args.workspace, args.cluster, auth, args.output_dir)
        print("Kubeconfig download completed successfully!")

    except EnvironmentError as e:
        print(f"Environment variable error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
