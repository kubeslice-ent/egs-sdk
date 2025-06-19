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
    Creates an Owner API key using the EGS_ACCESS_TOKEN.
    """
    access_token = get_env_variable("EGS_ACCESS_TOKEN")
    endpoint = get_env_variable("EGS_ENDPOINT")
    
    # Parse the endpoint URL
    parsed_url = urlparse(endpoint)
    host = parsed_url.netloc
    
    # Create connection
    connection = http.client.HTTPSConnection(host)
    
    # Prepare the request
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    
    payload = json.dumps({
        "name": "auto-generated-owner-key",
        "role": "Owner",
        "validity": "90d",
        "description": "Auto-generated Owner API key"
    })
    
    try:
        connection.request("POST", "/api/v1/api-keys", payload, headers)
        response = connection.getresponse()
        response_data = response.read().decode('utf-8')
        
        if response.status == 200:
            response_json = json.loads(response_data)
            return response_json.get('apiKey')
        else:
            raise Exception(f"Failed to create API key: {response.status} {response_data}")
    finally:
        connection.close()


def detach_cluster_from_workspace(workspace_name, cluster_name, auth):
    """
    Detaches a cluster from a workspace/slice.
    """
    try:
        print(f"🔍 Checking workspace '{workspace_name}' for cluster '{cluster_name}'...")
        
        # First, let's check if the workspace exists and contains the cluster
        workspaces = egs.list_workspaces(authenticated_session=auth)
        target_workspace = None
        
        for workspace in workspaces.workspaces:
            if workspace.name == workspace_name:
                target_workspace = workspace
                break
        
        if not target_workspace:
            raise ValueError(f"Workspace '{workspace_name}' not found")
        
        print(f"✅ Found workspace: {workspace_name}")
        print(f"   Current clusters: {target_workspace.clusters}")
        
        if cluster_name not in target_workspace.clusters:
            print(f"⚠️  Cluster '{cluster_name}' is not attached to workspace '{workspace_name}'")
            return None
        
        if len(target_workspace.clusters) <= 1:
            print(f"⚠️  Cannot detach the last cluster from workspace '{workspace_name}'. At least one cluster must remain.")
            return None
        
        print(f"🔄 Detaching cluster '{cluster_name}' from workspace '{workspace_name}'...")
        
        # Detach the cluster
        updated_workspace = egs.detach_cluster_from_workspace(
            workspace_name=workspace_name,
            cluster_name=cluster_name,
            authenticated_session=auth
        )
        
        print(f"✅ Successfully detached cluster '{cluster_name}' from workspace '{workspace_name}'")
        
        # Show updated workspace configuration
        updated_workspaces = egs.list_workspaces(authenticated_session=auth)
        for workspace in updated_workspaces.workspaces:
            if workspace.name == workspace_name:
                print(f"   Updated clusters: {workspace.clusters}")
                break
        
        return updated_workspace
        
    except Exception as e:
        print(f"❌ Error detaching cluster '{cluster_name}' from workspace '{workspace_name}': {str(e)}")
        raise


def attach_cluster_to_workspace(workspace_name, cluster_name, auth):
    """
    Attaches a cluster to a workspace/slice (for testing purposes).
    """
    try:
        print(f"🔄 Attaching cluster '{cluster_name}' to workspace '{workspace_name}'...")
        
        # Get current workspace details
        workspaces = egs.list_workspaces(authenticated_session=auth)
        target_workspace = None
        
        for workspace in workspaces.workspaces:
            if workspace.name == workspace_name:
                target_workspace = workspace
                break
        
        if not target_workspace:
            raise ValueError(f"Workspace '{workspace_name}' not found")
        
        if cluster_name in target_workspace.clusters:
            print(f"⚠️  Cluster '{cluster_name}' is already attached to workspace '{workspace_name}'")
            return None
        
        # Add the cluster to the list
        updated_clusters = target_workspace.clusters + [cluster_name]
        
        # Extract current namespaces
        current_namespaces = [ns.namespace for ns in target_workspace.namespaces]
        
        # Update the workspace
        updated_workspace = egs.update_workspace(
            workspace_name=workspace_name,
            clusters=updated_clusters,
            namespaces=current_namespaces,
            authenticated_session=auth
        )
        
        print(f"✅ Successfully attached cluster '{cluster_name}' to workspace '{workspace_name}'")
        return updated_workspace
        
    except Exception as e:
        print(f"❌ Error attaching cluster '{cluster_name}' to workspace '{workspace_name}': {str(e)}")
        raise


def show_workspace_details(workspace_name, auth):
    """
    Shows detailed information about a workspace.
    """
    try:
        workspaces = egs.list_workspaces(authenticated_session=auth)
        
        for workspace in workspaces.workspaces:
            if workspace.name == workspace_name:
                print(f"\n📋 Workspace Details: {workspace_name}")
                print(f"   🔧 Clusters: {workspace.clusters}")
                print(f"   📦 Namespaces: {[ns.namespace for ns in workspace.namespaces]}")
                print(f"   🌐 Overlay Network Mode: {workspace.overlay_network_deployment_mode}")
                print(f"   📝 Description: {workspace.slice_description}")
                print(f"   🎯 Max Clusters: {workspace.max_clusters}")
                return workspace
        
        print(f"❌ Workspace '{workspace_name}' not found")
        return None
        
    except Exception as e:
        print(f"❌ Error retrieving workspace details: {str(e)}")
        raise


def process_detach_operations(config, auth):
    """
    Processes detach operations from configuration file.
    """
    for operation in config.get("detach_operations", []):
        workspace_name = operation.get("workspace_name")
        cluster_name = operation.get("cluster_name")
        
        if not workspace_name or not cluster_name:
            print("⚠️  Skipping invalid detach operation - missing workspace_name or cluster_name")
            continue
        
        print(f"\n🎯 Processing detach operation:")
        print(f"   Workspace: {workspace_name}")
        print(f"   Cluster to detach: {cluster_name}")
        
        try:
            # Show current state
            show_workspace_details(workspace_name, auth)
            
            # Detach the cluster
            detach_cluster_from_workspace(workspace_name, cluster_name, auth)
            
            # Wait a moment
            time.sleep(2)
            
            # Show updated state
            show_workspace_details(workspace_name, auth)
            
        except Exception as e:
            print(f"❌ Failed to process detach operation: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Detach Cluster from Workspace/Slice - Manage cluster attachments"
    )
    parser.add_argument(
        "--config", help="Configuration file for batch detach operations"
    )
    parser.add_argument(
        "--workspace", help="Workspace name"
    )
    parser.add_argument(
        "--detach-cluster", help="Cluster name to detach from workspace"
    )
    parser.add_argument(
        "--attach-cluster", help="Cluster name to attach to workspace (for testing)"
    )
    parser.add_argument(
        "--show-details", action="store_true", help="Show detailed workspace information"
    )
    parser.add_argument(
        "--list", action="store_true", help="List all workspaces"
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
                ns_names = [ns.namespace for ns in ws.namespaces]
                print(f"  🏷️  {ws.name}:")
                print(f"      🔧 Clusters: {ws.clusters}")
                print(f"      📦 Namespaces: {ns_names}")
            exit(0)

        # Handle show workspace details
        if args.show_details and args.workspace:
            show_workspace_details(args.workspace, auth)
            exit(0)

        # Handle single workspace operations
        if args.workspace:
            if args.detach_cluster:
                print(f"🎯 Detaching cluster '{args.detach_cluster}' from workspace '{args.workspace}'")
                show_workspace_details(args.workspace, auth)
                detach_cluster_from_workspace(args.workspace, args.detach_cluster, auth)
                print("\n" + "="*50)
                show_workspace_details(args.workspace, auth)
                print("✅ Detach operation completed.")
                exit(0)
            
            if args.attach_cluster:
                print(f"🎯 Attaching cluster '{args.attach_cluster}' to workspace '{args.workspace}' (for testing)")
                show_workspace_details(args.workspace, auth)
                attach_cluster_to_workspace(args.workspace, args.attach_cluster, auth)
                print("\n" + "="*50)
                show_workspace_details(args.workspace, auth)
                print("✅ Attach operation completed.")
                exit(0)

        # Handle batch operations from configuration file
        if args.config:
            if not os.path.exists(args.config):
                raise FileNotFoundError(f"Configuration file not found: {args.config}")

            with open(args.config, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)

            if not config:
                raise ValueError("Configuration file is empty or invalid.")

            print("📋 Processing batch detach operations from configuration file...")
            process_detach_operations(config, auth)
            print("\n✅ All detach operations completed successfully!")
            exit(0)

        # If no specific operation is requested, show help
        print("❌ No operation specified. Use one of the following options:")
        print("  --list: List all workspaces")
        print("  --workspace <name> --show-details: Show workspace details")
        print("  --workspace <name> --detach-cluster <cluster>: Detach cluster from workspace")
        print("  --workspace <name> --attach-cluster <cluster>: Attach cluster to workspace")
        print("  --config <file>: Process batch operations from configuration file")
        print("Use --help for more information.")

    except ApiKeyInvalid as e:
        print("❌ API Key is Invalid")
        print(e)
    except ApiKeyNotFound as e:
        print("❌ API Key not found")
        print(e)
    except Exception as e:
        print(f"❌ Exception: {e}")
        raise 