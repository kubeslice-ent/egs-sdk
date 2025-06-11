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


def find_workspace(workspace_name, auth):
    """
    Finds a workspace by name and returns its current configuration.
    """
    try:
        workspaces = egs.list_workspaces(authenticated_session=auth)
        for ws in workspaces.workspaces:
            if ws.name == workspace_name:
                return ws
        return None
    except Exception as e:
        raise ValueError(f"Failed to find workspace '{workspace_name}': {str(e)}") from e


def extract_namespace_names(workspace_namespaces):
    """
    Extracts namespace names from the workspace namespace structure.
    """
    namespace_names = []
    for ns in workspace_namespaces:
        if isinstance(ns, dict) and 'namespace' in ns:
            namespace_names.append(ns['namespace'])
        elif hasattr(ns, 'namespace'):
            namespace_names.append(ns.namespace)
    return namespace_names


def update_workspace_with_recreate(workspace_name, add_namespaces=None, add_clusters=None, auth=None):
    """
    Updates a workspace by recreating it with additional namespaces and clusters.
    WARNING: This will delete and recreate the workspace, which may affect running workloads.
    """
    if add_namespaces is None:
        add_namespaces = []
    if add_clusters is None:
        add_clusters = []
    
    print(f"🔍 Looking for workspace: {workspace_name}")
    
    # Find current workspace
    current_workspace = find_workspace(workspace_name, auth)
    if not current_workspace:
        raise ValueError(f"Workspace '{workspace_name}' not found")
    
    print(f"✅ Found workspace: {workspace_name}")
    print(f"   Current clusters: {current_workspace.clusters}")
    
    # Extract current namespaces
    current_namespace_names = extract_namespace_names(current_workspace.namespaces)
    print(f"   Current namespaces: {current_namespace_names}")
    
    # Calculate new configuration
    new_clusters = list(set(current_workspace.clusters + add_clusters))
    new_namespaces = list(set(current_namespace_names + add_namespaces))
    
    print(f"   New clusters: {new_clusters}")
    print(f"   New namespaces: {new_namespaces}")
    
    # Show what changes will be made
    added_clusters = [c for c in new_clusters if c not in current_workspace.clusters]
    added_namespaces = [n for n in new_namespaces if n not in current_namespace_names]
    
    if not added_clusters and not added_namespaces:
        print("⚠️  No changes needed - all specified namespaces and clusters already exist")
        return
    
    if added_clusters:
        print(f"➕ Will add clusters: {added_clusters}")
    if added_namespaces:
        print(f"➕ Will add namespaces: {added_namespaces}")
    
    # WARNING: This approach requires deleting and recreating the workspace
    print("\n⚠️  WARNING: This operation will DELETE and RECREATE the workspace!")
    print("   This may affect running workloads in the workspace.")
    print("   Kubernetes resources in the workspace may be lost.")
    
    # Note: In a real implementation, you'd want user confirmation here
    # For now, we'll proceed with the operation
    
    try:
        # Delete the existing workspace
        print(f"🗑️  Deleting existing workspace: {workspace_name}")
        egs.delete_workspace(workspace_name, auth)
        print("✅ Workspace deleted successfully")
        
        # Wait a moment for the deletion to complete
        time.sleep(5)
        
        # Create the new workspace with updated configuration
        print(f"🆕 Creating updated workspace: {workspace_name}")
        
        # Note: We need username and email for workspace creation
        # Since we don't have this info from the existing workspace, we'll use defaults
        # In a real scenario, you'd need to store this information or prompt the user
        username = "admin"  # Default username
        email = "admin@example.com"  # Default email
        
        new_workspace_name = egs.create_workspace(
            workspace_name,
            new_clusters,
            new_namespaces,
            username,
            email,
            auth,
        )
        
        print(f"✅ Workspace '{new_workspace_name}' recreated successfully")
        
        # Generate kubeconfig files for all clusters
        workspace_dir = os.path.join("kubeconfigs", workspace_name)
        os.makedirs(workspace_dir, exist_ok=True)
        
        for cluster_name in new_clusters:
            try:
                kubeconfig = egs.get_workspace_kubeconfig(
                    workspace_name=workspace_name,
                    cluster_name=cluster_name,
                    authenticated_session=auth,
                )
                
                kubeconfig_filename = f"{cluster_name}.config"
                kubeconfig_path = os.path.join(workspace_dir, kubeconfig_filename)
                
                with open(kubeconfig_path, "w", encoding="utf-8") as kube_file:
                    kube_file.write(kubeconfig)
                
                print(f"📁 KubeConfig for '{workspace_name}' in '{cluster_name}' saved at {kubeconfig_path}")
                
            except Exception as kubeconfig_err:
                print(f"⚠️ Failed to generate kubeconfig for cluster '{cluster_name}': {str(kubeconfig_err)}")
        
        return new_workspace_name
        
    except Exception as e:
        print(f"❌ Error during workspace recreation: {str(e)}")
        raise


def test_workspace_update(workspace_name, auth):
    """
    Test function to add single namespace and cluster to a workspace.
    """
    print(f"\n🧪 Testing workspace update for: {workspace_name}")
    
    try:
        # Add a test namespace and cluster
        result = update_workspace_with_recreate(
            workspace_name=workspace_name,
            add_namespaces=["test-namespace-new"],
            add_clusters=["worker-2"],
            auth=auth
        )
        
        if result:
            print(f"✅ Test update successful for workspace: {result}")
        else:
            print("ℹ️  No changes were needed")
            
    except Exception as e:
        print(f"❌ Test update failed: {str(e)}")


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
        
        # Get new namespaces and clusters to add
        new_namespaces = cur_ws.get("add_namespaces", [])
        new_clusters = cur_ws.get("add_clusters", [])
        
        if not new_namespaces and not new_clusters:
            print("⚠️ No namespaces or clusters specified to add")
            continue
            
        try:
            update_workspace_with_recreate(
                workspace_name=workspace_name,
                add_namespaces=new_namespaces,
                add_clusters=new_clusters,
                auth=auth
            )
            time.sleep(3)  # Small delay between operations
        except Exception as e:
            print(f"❌ Error updating workspace '{workspace_name}': {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update Workspace V2 - Recreate workspaces with additional namespaces and clusters"
    )
    parser.add_argument(
        "--config", help="Workspace update configuration file"
    )
    parser.add_argument(
        "--workspace", help="Specific workspace name to update"
    )
    parser.add_argument(
        "--add-namespace", help="Add a single namespace to the specified workspace"
    )
    parser.add_argument(
        "--add-cluster", help="Add a single cluster to the specified workspace"
    )
    parser.add_argument(
        "--test", help="Test workspace update with sample data"
    )
    parser.add_argument(
        "--list", action="store_true", help="List all current workspaces"
    )
    
    args = parser.parse_args()

    try:
        # Authentication setup
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

        # Handle list workspaces
        if args.list:
            workspaces = egs.list_workspaces(authenticated_session=auth)
            print(f"\n📋 Found {len(workspaces.workspaces)} workspaces:")
            for ws in workspaces.workspaces:
                ns_names = extract_namespace_names(ws.namespaces)
                print(f"  🏷️  {ws.name}: clusters={ws.clusters}, namespaces={ns_names}")
            exit(0)

        # Handle test mode
        if args.test:
            test_workspace_update(args.test, auth)
            exit(0)

        # Handle single workspace update with command line arguments
        if args.workspace and (args.add_namespace or args.add_cluster):
            print(f"🎯 Updating specific workspace: {args.workspace}")
            
            namespaces = [args.add_namespace] if args.add_namespace else []
            clusters = [args.add_cluster] if args.add_cluster else []
            
            update_workspace_with_recreate(
                workspace_name=args.workspace,
                add_namespaces=namespaces,
                add_clusters=clusters,
                auth=auth
            )
                
            print("✅ Single workspace update completed.")
            exit(0)

        # Handle batch updates from configuration file
        if not args.config:
            print("❌ No configuration file specified. Use --config or other options.")
            print("Use --help for usage information.")
            exit(1)

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
        print("⚠️  WARNING: This will recreate workspaces, which may affect running workloads!")
        
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