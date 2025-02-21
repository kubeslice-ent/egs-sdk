
import egs
from egs.internal.workspace.list_workspaces_data import ListWorkspacesResponse
from egs.exceptions import ApiKeyInvalid, ApiKeyNotFound, WorkspaceAlreadyExists


from kubernetes import client, config
import argparse
import os
import sys
import yaml
import time
import base64


def get_env_variable(env_name):
    """
    Fetches the value of an environment variable.
    Throws an error if the variable is not set.
    """
    value = os.getenv(env_name)
    if value is None:
        raise EnvironmentError(f"Environment variable '{env_name}' is not set.")
    return value


def get_kubeconfig_secret(workspace_name, project_name):
    """
    Retrieves the token from the Kubernetes secret.
    """
    try:
        v1 = client.CoreV1Api()
        secret_name = f"kubeslice-rbac-rw-slice-{workspace_name}"
        secret = v1.read_namespaced_secret(name=secret_name, namespace=project_name)
        token_b64 = secret.data.get("token")
        if token_b64:
            return base64.b64decode(token_b64).decode("utf-8")
        else:
            raise ValueError("Token not found in secret")
    except Exception as e:
        raise ValueError(f"Failed to retrieve token for {workspace_name}: {str(e)}")


# Example usage
if __name__ == "__main__":
    # Set up command-line arguments
    parser = argparse.ArgumentParser(
                    description="Create Workspace Options")

    parser.add_argument("--config",
                        required=True,
                        help="Workspace configuration")

    args = parser.parse_args()

    try:
        # # Authenticate the EGS
        auth = egs.authenticate(get_env_variable('EGS_ENDPOINT'),
                                api_key=get_env_variable('EGS_API_KEY'),
                                sdk_default=False)

        if not args.config:
            raise ValueError("Configuration file path must be provided using --config argument.")

        if not os.path.exists(args.config):
            raise FileNotFoundError(f"Missing the workspace configuration {args.config}")

        try:
            with open(args.config, "r", encoding="utf-8") as file:
                workspace_config = yaml.safe_load(file)
                if not workspace_config or 'workspaces' not in workspace_config:
                    raise ValueError("Workspace configuration file is empty or invalid.")
        except yaml.YAMLError as e:
            raise ValueError(f"Error loading workspace configuration file: {str(e)}")

        config.load_kube_config()

        for cur_ws in workspace_config.get('workspaces', []):
            if not all(key in cur_ws for key in ['name',
                                                 'clusters',
                                                 'namespaces',
                                                 'username',
                                                 'email']):
                print(f"Skipping invalid workspace entry: {cur_ws}")
                continue

            workspace_name = egs.create_workspace(
                cur_ws['name'],
                cur_ws['clusters'],
                cur_ws['namespaces'],
                cur_ws['username'],
                cur_ws['email'],
                auth
            )
            print(f"Workspace created: {workspace_name}")
            workspace_dir = os.path.join("kubeconfigs", workspace_name)
            os.makedirs(workspace_dir, exist_ok=True)
            time.sleep(10)

            for cluster_name in cur_ws['clusters']:
                try:
                    kubeconfig = egs.get_workspace_kubeconfig(
                        workspace_name=workspace_name,
                        cluster_name=cluster_name,
                        authenticated_session=auth
                    )

                except Exception as e:
                    print(f"Failed to retrive KubeConfig for {workspace_name} workspace {cluster_name} cluster")
                    raise ValueError(f"Failed to retrive KubeConfig for {workspace_name} workspace {cluster_name} cluster")
                try:
                    kubeconfig_filename = f"{cluster_name}.config"
                    kubeconfig_path = os.path.join(workspace_dir, kubeconfig_filename)
                    with open(kubeconfig_path, "w", encoding="utf-8") as kube_file:
                        kube_file.write(kubeconfig)
                    print(f"KubeConfig for {workspace_name} in {cluster_name} saved at {kubeconfig_path}")
                except Exception as e:
                    print(f"Failed to save KubeConfig for {workspace_name} workspace {cluster_name} cluster")
                    raise ValueError(f"Failed to save KubeConfig for {workspace_name} workspace {cluster_name} cluster")

            try:
                # Create API key
                response = egs.create_api_key(
                    name=cur_ws['name'],
                    role='Editor',
                    valid_until=cur_ws['validUntil'],
                    username=cur_ws['username'],
                    description=f"API Key for {cur_ws['name']}",
                    slice_name=cur_ws['name']
                )

                print(f"✅ Successfully created API key: {cur_ws['name']} api-key {response}")

            except (ApiKeyInvalid, ApiKeyNotFound, ValueError) as e:
                print(f"⚠️ Error creating API key {cur_ws['name']}: {e}")
            except Exception as e:
                print(f"❌ Unexpected error for {cur_ws['name']}: {e}")

            # Retrieve and save the token
            try:
                project_name = f'kubeslice-{workspace_config.get("projectname")}'
                token = get_kubeconfig_secret(workspace_name, project_name)
                token_path = os.path.join(workspace_dir, "token.txt")
                with open(token_path, "w", encoding="utf-8") as token_file:
                    token_file.write(token)
                print(f"Token for {workspace_name} saved at {token_path}")
            except Exception as e:
                print(f"Failed to retrieve and save token for {workspace_name}")
                raise ValueError(f"Failed to retrieve and save token for {workspace_name}: {str(e)}")

    except ApiKeyInvalid as e:
        # Do something when API key is not found
        print("API Key is Invalid")
        print(e)
    except ApiKeyNotFound as e:
        # Do something when API key is not found
        print("API Key not found")
        print(e)
    except WorkspaceAlreadyExists as e:
        # Do something when API key is not found
        print("WorkspaceAlreadyExists found")
        print(e)
    except Exception as e:
        print(e)
        print(f"Exception: {e}")
        # sys.exit(1)
