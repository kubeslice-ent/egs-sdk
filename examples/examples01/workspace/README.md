# Workspace Management Scripts

This folder contains scripts for managing workspaces using the EGS SDK.

## Scripts Overview

### 1. create_workspace.py
Creates a workspace with basic configuration.

**Usage:**
```bash
python create_workspace.py --workspace_name "tezz-slice" --clusters "worker-1,worker-2" --namespaces "nim,locust" --username "admin" --email "admin@example.com"
```

**Features:**
- Creates a new workspace
- Configures clusters and namespaces
- Sets up user access

### 2. delete_workspace.py
Deletes a workspace and cleans up associated resources.

**Usage:**
```bash
python delete_workspace.py --config workspace_config.yaml
```

**Features:**
- Deletes API keys associated with the workspace
- Removes the workspace completely
- Uses YAML configuration file for batch operations

### 3. create_workspace_with_auto_gpr.py
Creates a workspace with automatic GPR (GPU Request) functionality enabled.

**Usage:**
```bash
python create_workspace_with_auto_gpr.py --workspace_name "tezz-slice" --clusters "worker-1,worker-2" --namespaces "nim,locust" --username "admin" --email "admin@example.com"
```

**Features:**
- Creates workspace with basic configuration
- Sets up GPR templates for each cluster
- Binds GPR templates to enable auto-GPR functionality
- Automatically handles GPU resource allocation

### 4. download_kubeconfig.py
Downloads kubeconfig files for specific clusters in a workspace.

**Usage:**
```bash
python download_kubeconfig.py --workspace "tezz-slice" --cluster "worker-1"
```

**Features:**
- Downloads kubeconfig for specific cluster
- Saves to workspace-specific directory
- Default output directory is script location



### 6. workspace_config.yaml
Configuration file for workspace operations.

**Structure:**
```yaml
projectname: "avesha"
workspaces:
  - name: "payload"
    namespaces:
      - "nim"
      - "locust"
    username: "admin-1"
    email: "admin1@avesha.io"
    clusters:
      - "worker-1"
      - "worker-2"
    apiKeyValidity: "2026-12-31"
```

## Common Parameters

- `--workspace_name`: Name of the workspace to create
- `--clusters`: Comma-separated list of cluster names
- `--namespaces`: Comma-separated list of namespace names
- `--username`: Username for the workspace
- `--email`: Email address for the workspace
- `--config`: Path to YAML configuration file

## Environment Variables Required

- `EGS_ENDPOINT`: EGS API endpoint
- `EGS_API_KEY`: EGS API key for authentication
- `EGS_ACCESS_TOKEN`: EGS access token (for creating owner API keys)

## Workflow

1. **Create Workspace**: Use `create_workspace.py` for basic workspace setup
2. **Enable Auto-GPR**: Use `create_workspace_with_auto_gpr.py` for GPU-enabled workspaces
3. **Download Access**: Use `download_kubeconfig.py` to get cluster access
4. **Cleanup**: Use `delete_workspace.py` when workspace is no longer needed

## Output

- **create_workspace.py**: Creates workspace and returns workspace name
- **delete_workspace.py**: Removes workspace and associated resources
- **create_workspace_with_auto_gpr.py**: Creates workspace with GPR templates and bindings
- **download_kubeconfig.py**: Downloads kubeconfig files to local directory
