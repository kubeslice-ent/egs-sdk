import os
import time
import argparse
import yaml
import json
import http.client
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

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
        "description": "OwnerAPIKey to update workspaces",
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


def add_namespace_to_workspace(workspace_name, namespace, auth):
    """
    Adds a new namespace to an existing workspace.
    """
    try:
        # Assuming there's an egs function to add namespace to workspace
        # If not available, we might need to get workspace details, modify them, and update
        response = egs.add_namespace_to_workspace(
            workspace_name=workspace_name,
            namespace=namespace,
            authenticated_session=auth
        )
        print(f"✅ Successfully added namespace '{namespace}' to workspace '{workspace_name}'")
        return response
    except Exception as e:
        # Fallback: Try to update workspace with additional namespace
        try:
            # Get current workspace details
            workspace_details = egs.get_workspace(workspace_name, auth)
            current_namespaces = workspace_details.get('namespaces', [])
            
            if namespace not in current_namespaces:
                current_namespaces.append(namespace)
                
                # Update workspace with new namespace list
                updated_workspace = egs.update_workspace(
                    workspace_name=workspace_name,
                    namespaces=current_namespaces,
                    authenticated_session=auth
                )
                print(f"✅ Successfully added namespace '{namespace}' to workspace '{workspace_name}'")
                return updated_workspace
            else:
                print(f"⚠️ Namespace '{namespace}' already exists in workspace '{workspace_name}'")
                return None
        except Exception as fallback_err:
            raise ValueError(
                f"Failed to add namespace '{namespace}' to workspace '{workspace_name}': {str(fallback_err)}"
            ) from fallback_err


def add_cluster_to_workspace(workspace_name, cluster_name, auth):
    """
    Adds a new cluster to an existing workspace.
    """
    try:
        # Assuming there's an egs function to add cluster to workspace
        response = egs.add_cluster_to_workspace(
            workspace_name=workspace_name,
            cluster_name=cluster_name,
            authenticated_session=auth
        )
        print(f"✅ Successfully added cluster '{cluster_name}' to workspace '{workspace_name}'")
        return response
    except Exception as e:
        # Fallback: Try to update workspace with additional cluster
        try:
            # Get current workspace details
            workspace_details = egs.get_workspace(workspace_name, auth)
            current_clusters = workspace_details.get('clusters', [])
            
            if cluster_name not in current_clusters:
                current_clusters.append(cluster_name)
                
                # Update workspace with new cluster list
                updated_workspace = egs.update_workspace(
                    workspace_name=workspace_name,
                    clusters=current_clusters,
                    authenticated_session=auth
                )
                print(f"✅ Successfully added cluster '{cluster_name}' to workspace '{workspace_name}'")
                
                # Generate kubeconfig for the new cluster
                try:
                    kubeconfig = egs.get_workspace_kubeconfig(
                        workspace_name=workspace_name,
                        cluster_name=cluster_name,
                        authenticated_session=auth,
                    )
                    
                    # Save kubeconfig to file
                    workspace_dir = os.path.join("kubeconfigs", workspace_name)
                    os.makedirs(workspace_dir, exist_ok=True)
                    
                    kubeconfig_filename = f"{cluster_name}.config"
                    kubeconfig_path = os.path.join(workspace_dir, kubeconfig_filename)
                    
                    with open(kubeconfig_path, "w", encoding="utf-8") as kube_file:
                        kube_file.write(kubeconfig)
                    
                    print(f"📁 KubeConfig for '{workspace_name}' in '{cluster_name}' saved at {kubeconfig_path}")
                    
                except Exception as kubeconfig_err:
                    print(f"⚠️ Failed to generate kubeconfig for cluster '{cluster_name}': {str(kubeconfig_err)}")
                
                return updated_workspace
            else:
                print(f"⚠️ Cluster '{cluster_name}' already exists in workspace '{workspace_name}'")
                return None
                
        except Exception as fallback_err:
            raise ValueError(
                f"Failed to add cluster '{cluster_name}' to workspace '{workspace_name}': {str(fallback_err)}"
            ) from fallback_err


def process_workspace_updates(workspace_config, auth):
    """
    Processes workspace updates from the configuration file.
    """
    for cur_ws in workspace_config.get("workspaces", []):
        workspace_name = cur_ws.get("name")
        if not workspace_name:
            print("⚠️ Skipping workspace entry without name")
            continue
            
        print(f"\n🔄 Processing updates for workspace: {workspace_name}")
        
        # Add new namespaces if specified
        new_namespaces = cur_ws.get("add_namespaces", [])
        for namespace in new_namespaces:
            try:
                add_namespace_to_workspace(workspace_name, namespace, auth)
                time.sleep(2)  # Small delay between operations
            except Exception as e:
                print(f"❌ Error adding namespace '{namespace}' to '{workspace_name}': {str(e)}")
        
        # Add new clusters if specified
        new_clusters = cur_ws.get("add_clusters", [])
        for cluster_name in new_clusters:
            try:
                add_cluster_to_workspace(workspace_name, cluster_name, auth)
                time.sleep(2)  # Small delay between operations
            except Exception as e:
                print(f"❌ Error adding cluster '{cluster_name}' to '{workspace_name}': {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update Workspace - Add namespaces and clusters to existing workspaces"
    )
    parser.add_argument(
        "--config", required=True, help="Workspace update configuration file"
    )
    parser.add_argument(
        "--workspace", help="Specific workspace name to update (optional)"
    )
    parser.add_argument(
        "--add-namespace", help="Add a single namespace to the specified workspace"
    )
    parser.add_argument(
        "--add-cluster", help="Add a single cluster to the specified workspace"
    )
    
    args = parser.parse_args()

    try:
        # Authentication setup (same pattern as create/delete scripts)
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

        # Handle single workspace update with command line arguments
        if args.workspace and (args.add_namespace or args.add_cluster):
            print(f"🎯 Updating specific workspace: {args.workspace}")
            
            if args.add_namespace:
                add_namespace_to_workspace(args.workspace, args.add_namespace, auth)
            
            if args.add_cluster:
                add_cluster_to_workspace(args.workspace, args.add_cluster, auth)
                
            print("✅ Single workspace update completed.")
            exit(0)

        # Handle batch updates from configuration file
        if not os.path.exists(args.config):
            raise FileNotFoundError(
                f"Missing workspace update configuration {args.config}"
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

        print("📋 Processing workspace updates from configuration file...")
        process_workspace_updates(workspace_config, auth)
        print("\n✅ All workspace updates completed successfully!")

    except ApiKeyInvalid as e:
        print("❌ API Key is Invalid")
        print(e)
    except ApiKeyNotFound as e:
        print("❌ API Key not found")
        print(e)
    except Exception as e:
        print(f"❌ Exception: {e}")
        raise 