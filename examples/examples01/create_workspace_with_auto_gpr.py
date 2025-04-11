import os
import time
import base64
import argparse
import yaml
import json
import http.client
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
from kubernetes import client, config

import egs
from egs.exceptions import (
    ApiKeyInvalid, ApiKeyNotFound, WorkspaceAlreadyExists
)


def get_env_variable(env_name):
    """
    Fetches the value of an environment variable.
    Throws an error if the variable is not set.
    """
    value = os.getenv(env_name)
    if value is None:
        raise EnvironmentError(
            f"Environment variable '{env_name}' is not set."
        )
    return value


def get_kubeconfig_secret(workspace_name, project_name):
    """
    Retrieves the token from the Kubernetes secret.
    """
    try:
        v1 = client.CoreV1Api()
        secret_name = f"kubeslice-rbac-rw-slice-{workspace_name}"
        secret = v1.read_namespaced_secret(
            name=secret_name, namespace=project_name
        )
        token_b64 = secret.data.get("token")
        if token_b64:
            return base64.b64decode(token_b64).decode("utf-8")
        raise ValueError("Token not found in secret")
    except Exception as e:
        raise ValueError(
            f"Failed to retrieve token for {workspace_name}: {str(e)}"
        ) from e


def create_owner_api_key():
    """
    Creates an Owner API Key using the EGS_ACCESS_TOKEN.
    """
    egs_endpoint = get_env_variable("EGS_ENDPOINT")
    egs_token = get_env_variable("EGS_ACCESS_TOKEN")

    # Parse the URL to extract host and path
    parsed_url = urlparse(egs_endpoint)
    host = parsed_url.netloc
    scheme = parsed_url.scheme
    path = "/api/v1/api-key"

    # Calculate validity (current date + 1 day) and format as "YYYY-MM-DD"
    validity = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")

    req_body = {
        "name": "OwnerAPIKey",
        "userName": "admin",
        "description": "OwnerAPIKey to create workspaces",
        "role": "Owner",
        "validity": validity,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {egs_token}",
    }

    # Use HTTP or HTTPS connection
    conn = http.client.HTTPSConnection(host) if scheme == "https" else http.client.HTTPConnection(host)

    try:
        conn.request("POST", path, body=json.dumps(req_body), headers=headers)
        resp = conn.getresponse()
        response_data = json.loads(resp.read().decode())

        if resp.status != 200:
            raise ValueError(f"❌ Failed to create Owner API Key: {resp.status} {response_data}")

        owner_api_key = response_data.get("data", {}).get("apiKey")

        if not owner_api_key:
            raise ValueError(f"❌ API key not found in response: {response_data}")

        print("✅ Successfully created Owner API Key.")
        return owner_api_key

    except Exception as err:
        raise RuntimeError(f"❌ Error creating API key: {err}") from err
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create Workspace Options"
    )
    parser.add_argument(
        "--config", required=True, help="Workspace configuration"
    )
    args = parser.parse_args()

    try:
        api_key = os.getenv("EGS_API_KEY")
        access_token = os.getenv("EGS_ACCESS_TOKEN")

        if not api_key:
            if access_token:
                print("🔑 EGS_API_KEY not found. Creating Owner API Key using EGS_ACCESS_TOKEN...")
                api_key = create_owner_api_key()
            else:
                raise ValueError(
                    "Either EGS_API_KEY or EGS_ACCESS_TOKEN must be set in the environment."
                )

        print("Using API Key for authentication.")
        auth = egs.authenticate(get_env_variable("EGS_ENDPOINT"),
                                api_key=api_key,
                                sdk_default=False)
        if not os.path.exists(args.config):
            raise FileNotFoundError(
                f"Missing workspace configuration {args.config}"
            )

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

        config.load_kube_config()

        for cur_ws in workspace_config.get("workspaces", []):
            required_keys = ["name", "clusters", "namespaces",
                             "username", "email"]
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
                    kubeconfig_path = os.path.join(
                        workspace_dir, kubeconfig_filename
                    )
                    with open(kubeconfig_path,
                              "w",
                              encoding="utf-8") as kube_file:
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
                                            workspace_name,
                                            authenticated_session=auth)
                    cur_inventory = inventory.workspace_inventory[0]
                    print(f"Creating GPR Template for {cluster_name}")
                    response = egs.create_gpr_template(
                                    name=cur_ws["name"]+'-'+cluster_name,
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
                                    authenticated_session=auth)

                    # response = egs.create_gpr_template(
                    #                 name=cur_ws["name"]+'-'+cluster_name,
                    #                 cluster_name=cluster_name,
                    #                 gpu_per_node_count=cur_inventory.gpu_per_node,
                    #                 num_gpu_nodes=1,
                    #                 memory_per_gpu=cur_inventory.memory_per_gpu,
                    #                 gpu_shape=cur_inventory.gpu_shape,
                    #                 instance_type=cur_inventory.instance_type,
                    #                 exit_duration="5m",
                    #                 priority=201,
                    #                 enforce_idle_timeout=False,
                    #                 enable_eviction=True,
                    #                 requeue_on_failure=True,
                    #                 authenticated_session=auth)
                    print(f"✅ Successfully Created GPR Template: {response}")
                    gpr_template_name = response
                    template_resp = egs.get_gpr_template(gpr_template_name, auth)
                    print(f"✅ Successfully Got GPR Template: {template_resp}")

                    # template_resp1 = egs.update_gpr_template(
                    #                     name=template_resp.name,
                    #                     cluster_name=template_resp.cluster_name,
                    #                     number_of_gpus=template_resp.number_of_gpus,
                    #                     instance_type=template_resp.instance_type,
                    #                     exit_duration="6m",
                    #                     number_of_gpu_nodes=template_resp.number_of_gpu_nodes,
                    #                     priority=template_resp.priority,
                    #                     memory_per_gpu=template_resp.memory_per_gpu,
                    #                     gpu_shape=template_resp.gpu_shape,
                    #                     enable_eviction=template_resp.enable_eviction,
                    #                     requeue_on_failure=template_resp.requeue_on_failure,
                    #                     enforce_idle_timeout=False, #template_resp.enforce_idle_timeout,
                    #                     authenticated_session=auth)
                    # print(f"✅ Successfully Updated GPR Template: {template_resp1}")

                    # template_resp = egs.get_gpr_template(gpr_template_name, auth)
                    # print(f"✅ Successfully Got GPR Template: {template_resp}")

                    # responses = egs.list_gpr_templates(auth)
                    # print(f"✅ Successfully Got List of GPR Template: {responses}")

                    # del_resp = egs.delete_gpr_template(gpr_template_name, auth)
                    # print(f"✅ Successfully Deleted GPR Template: {del_resp}")
                except Exception as e:
                    print(f"❌ Unexpected error for {cur_ws['name']}: {e}")
                
                # Bind the Template to workspace
                try:
                    print(f"Bind the {gpr_template_name} Template to workspace {workspace_name}")
                    cluster_dict = {
                                        "clusterName": cluster_name,
                                        "defaultTemplateName": gpr_template_name,
                                        "templates": [gpr_template_name]
                                    }
                    response = egs.create_gpr_template_binding(
                                        workspace_name=workspace_name,
                                        clusters=[cluster_dict],
                                        enable_auto_gpr=True,
                                        authenticated_session=auth)

                    print(f"✅ Successfully Created GPR Template Binding: {response}")
                    gpr_template_binding_name = response.name
                    template_resp2 = egs.get_gpr_template_binding(
                                            gpr_template_binding_name,
                                            auth)
                    print(f"✅ Successfully Got GPR Template Binding: {template_resp2}")

                    update_resp = egs.update_gpr_template_binding(
                                    workspace_name=workspace_name,
                                    clusters=[cluster_dict],
                                    enable_auto_gpr=False,
                                    authenticated_session=auth)
                    print(f"✅ Successfully Updated GPR Template Binding: {update_resp}")

                    template_resp3 = egs.get_gpr_template_binding(
                                                gpr_template_binding_name,
                                                auth)
                    print(f"✅ Successfully Got GPR Template Binding: {template_resp3}")

                    # responses = egs.list_gpr_templates(auth)
                    # print(f"✅ Successfully Got List of GPR Template: {responses}")

                    del_resp1 = egs.delete_gpr_template_binding(gpr_template_binding_name, auth)
                    print(f"✅ Successfully Deleted GPR Template Binding: {del_resp1}")
                except Exception as e:
                    print(f"❌ Unexpected error for {cur_ws['name']}: {e}")


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
                    with open(apikey_path,
                              "w",
                              encoding="utf-8") as apikey_file:
                        apikey_file.write(response)
                    print(
                        f"✅ Successfully Saved API key: {cur_ws['name']} "
                        f"api-key {response}"
                    )
                except Exception as e:
                    print(f"Failed to save token for {cur_ws['name']}")
                    raise ValueError(
                        f"Failed to save token for {cur_ws['name']}: {str(e)}"
                    ) from e

            except (ApiKeyInvalid, ApiKeyNotFound, ValueError) as e:
                print(f"⚠️ Error creating API key {cur_ws['name']}: {e}")
            except Exception as e:
                print(f"❌ Unexpected error for {cur_ws['name']}: {e}")



            # try:
            #     project_name = f"kubeslice-{workspace_config.get('projectname')}"
            #     token = get_kubeconfig_secret(workspace_name, project_name)
            #     token_path = os.path.join(workspace_dir, "token.txt")
            #     with open(token_path, "w", encoding="utf-8") as token_file:
            #         token_file.write(token)
            #     print(f"Token for {workspace_name} saved at {token_path}")
            # except Exception as e:
            #     print(f"Failed to retrieve and save token for {workspace_name}")
            #     raise ValueError(
            #         f"Failed to retrieve and save token for {workspace_name}: {str(e)}"
            #     ) from e

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
