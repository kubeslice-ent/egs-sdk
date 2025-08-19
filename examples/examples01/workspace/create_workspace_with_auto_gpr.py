import argparse
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
import egs
from egs.exceptions import ApiKeyInvalid, ApiKeyNotFound, WorkspaceAlreadyExists


def get_env_variable(env_name):
    """
    Fetches the value of an environment variable.
    Throws an error if the variable is not set.
    """
    value = os.getenv(env_name)
    if value is None:
        raise EnvironmentError(f"Environment variable '{env_name}' is not set.")
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create Workspace Options")
    parser.add_argument("--config", required=True, help="Workspace configuration")
    args = parser.parse_args()

    try:
        api_key = os.getenv("EGS_API_KEY")
        access_token = os.getenv("EGS_ACCESS_TOKEN")
        egs_endpoint = get_env_variable("EGS_ENDPOINT")

        if not api_key:
            if access_token:
                print(
                    "EGS_API_KEY not found. Creating Owner API Key using EGS_ACCESS_TOKEN..."
                )

                api_key = egs.create_owner_api_key(
                    egs_endpoint=egs_endpoint,
                    egs_token=access_token,
                    name="OwnerApiKey",
                    description="OwnerAPIKey to create workspaces",
                    username="admin",
                )
            else:
                raise ValueError(
                    "Either EGS_API_KEY or EGS_ACCESS_TOKEN must be set in the environment."
                )

        print("Using API Key for authentication.")
        auth = egs.authenticate(egs_endpoint, api_key=api_key, sdk_default=False)
        if not os.path.exists(args.config):
            raise FileNotFoundError(f"Missing workspace configuration {args.config}")

        try:
            with open(args.config, "r", encoding="utf-8") as file:
                workspace_config = yaml.safe_load(file)
                if not workspace_config or "workspaces" not in workspace_config:
                    raise ValueError(
                        "Workspace configuration file is empty or invalid."
                    )
        except yaml.YAMLError as e:
            raise ValueError(
                f"Error loading workspace configuration file: {str(e)}"
            ) from e

        for cur_ws in workspace_config.get("workspaces", []):
            required_keys = ["name", "clusters", "namespaces", "username", "email"]
            if not all(key in cur_ws for key in required_keys):
                print(f"Skipping invalid workspace entry: {cur_ws}")
                continue

            workspace_name = egs.create_workspace(
                cur_ws["name"],
                cur_ws["clusters"],
                cur_ws["namespaces"],
                cur_ws["username"],
                cur_ws["email"],
                auth,
            )
            print(f"Workspace created: {workspace_name}")
            workspace_dir = os.path.join("kubeconfigs", workspace_name)
            os.makedirs(workspace_dir, exist_ok=True)
            time.sleep(10)

            # Collect all cluster configurations for GPR template binding
            all_clusters_config = []

            for cluster_name in cur_ws["clusters"]:
                try:
                    kubeconfig = egs.get_workspace_kubeconfig(
                        workspace_name=workspace_name,
                        cluster_name=cluster_name,
                        authenticated_session=auth,
                    )
                except Exception as e:
                    print(
                        f"Failed to retrieve KubeConfig for {workspace_name} "
                        f"workspace {cluster_name} cluster: {str(e)}"
                    )
                    raise ValueError(
                        f"Failed to retrieve KubeConfig for {workspace_name} "
                        f"workspace {cluster_name} cluster"
                    ) from e

                try:
                    kubeconfig_filename = f"{cluster_name}.config"
                    kubeconfig_path = os.path.join(workspace_dir, kubeconfig_filename)
                    with open(kubeconfig_path, "w", encoding="utf-8") as kube_file:
                        kube_file.write(kubeconfig)
                    print(
                        f"KubeConfig for {workspace_name} in {cluster_name} "
                        f"saved at {kubeconfig_path}"
                    )
                except Exception as e:
                    print(
                        f"Failed to save KubeConfig for {workspace_name} "
                        f"workspace {cluster_name} cluster: {str(e)}"
                    )
                    raise ValueError(
                        f"Failed to save KubeConfig for {workspace_name} "
                        f"workspace {cluster_name} cluster"
                    ) from e

                try:
                    # Get the Inventory
                    inventory = egs.workspace_inventory(
                        workspace_name, authenticated_session=auth
                    )
                    cur_inventory = inventory.workspace_inventory[0]
                    print(
                        f"Creating GPR Template for {cluster_name} using inventory {cur_inventory}"
                    )
                    response = egs.create_gpr_template(
                        name=cur_ws["name"] + "-" + cluster_name,
                        cluster_name=cluster_name,
                        gpu_per_node_count=cur_inventory.gpu_per_node,
                        num_gpu_nodes=1,
                        memory_per_gpu=cur_inventory.memory_per_gpu,
                        gpu_shape=cur_inventory.gpu_shape,
                        instance_type=cur_inventory.instance_type,
                        exit_duration="5m",
                        priority=201,
                        enforce_idle_timeout=True,
                        enable_eviction=True,
                        requeue_on_failure=True,
                        idle_timeout_duration="2m",
                        authenticated_session=auth,
                    )

                    print(f"Successfully Created GPR Template: {response}")
                    gpr_template_name = response

                    # Add cluster configuration to the list
                    cluster_dict = {
                        "clusterName": cluster_name,
                        "defaultTemplateName": gpr_template_name,
                        "templates": [gpr_template_name],
                    }
                    all_clusters_config.append(cluster_dict)

                except Exception as e:
                    print(
                        f"Failed to create GPR template for {cur_ws['name']} cluster {cluster_name}: {e}"
                    )
                    raise RuntimeError(
                        f"GPR template creation failed for workspace '{cur_ws['name']}' cluster '{cluster_name}': {e}"
                    )

            # Create single GPR template binding for all clusters in the workspace
            try:
                print(
                    f"Creating GPR Template Binding for workspace {workspace_name} with {len(all_clusters_config)} clusters"
                )
                binding_resp = egs.create_gpr_template_binding(
                    workspace_name=workspace_name,
                    clusters=all_clusters_config,
                    enable_auto_gpr=True,
                    authenticated_session=auth,
                )

                print(f"Successfully Created GPR Template Binding: {binding_resp}")
                gpr_template_binding_name = binding_resp.name

            except Exception as e:
                print(
                    f"Failed to create GPR template binding for workspace {workspace_name}: {e}"
                )
                raise RuntimeError(
                    f"GPR template binding failed for workspace '{workspace_name}': {e}"
                )

            try:
                response = egs.create_api_key(
                    name=cur_ws["name"],
                    role="Editor",
                    validity=cur_ws["apiKeyValidity"],
                    username=cur_ws["username"],
                    description=f"API Key for {cur_ws['name']}",
                    workspace_name=cur_ws["name"],
                    authenticated_session=auth,
                )

                try:
                    apikey_path = os.path.join(workspace_dir, "apikey.txt")
                    with open(apikey_path, "w", encoding="utf-8") as apikey_file:
                        apikey_file.write(response)
                    print(
                        f"Successfully Saved API key: {cur_ws['name']} "
                        f"api-key {response}"
                    )
                except Exception as e:
                    print(f"Failed to save token for {cur_ws['name']}")
                    raise ValueError(
                        f"Failed to save token for {cur_ws['name']}: {str(e)}"
                    ) from e

            except (ApiKeyInvalid, ApiKeyNotFound, ValueError) as e:
                print(f"Error creating API key {cur_ws['name']}: {e}")
            except Exception as e:
                print(f"Unexpected error for {cur_ws['name']}: {e}")

    except ApiKeyInvalid as e:
        print("API Key is Invalid")
        print(e)
    except ApiKeyNotFound as e:
        print("API Key not found")
        print(e)
    except WorkspaceAlreadyExists as e:
        print("WorkspaceAlreadyExists")
        print(e)
    except Exception as e:
        print(e)
        print(f"Exception: {e}")
