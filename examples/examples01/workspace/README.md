# Workspace Management Scripts

This folder contains scripts for managing workspaces using the EGS SDK.

## Environment Variables Required

- `EGS_ENDPOINT`: EGS API endpoint (required)
- `EGS_API_KEY`: EGS API key for authentication (if available)
- `EGS_ACCESS_TOKEN`: EGS access token (required if EGS_API_KEY is not set)

**Note:** The script will automatically create an owner API key using `EGS_ACCESS_TOKEN` if `EGS_API_KEY` is not provided.

## Workspace Configuration

### workspace_config.yaml
Configuration file for workspace operations.

**Structure:**
```yaml
projectname: "avesha"
workspaces:
  - name: "payload"
    namespaces:
      - "fffff"
    username: "admin-1"
    email: "admin1@avesha.io"
    clusters:
      - "worker-1"
      - "worker-2"
    apiKeyValidity: "2026-12-31"
```

**Required Fields:**
- `name`: Workspace name
- `namespaces`: List of namespace names
- `username`: Username for the workspace
- `email`: Email address for the workspace
- `clusters`: List of cluster names
- `apiKeyValidity`: API key expiration date

## Scripts Overview

### 1. create_workspace.py
Creates a workspace with basic configuration.

**Usage:**
```bash
python create_workspace.py --workspace_name "tezz-slice" --clusters "worker-1,worker-2" --namespaces "nim,locust" --username "admin" --email "admin@example.com"
```

**Arguments:**
- `--workspace_name`: Name of the workspace to create
- `--clusters`: Comma-separated list of cluster names
- `--namespaces`: Comma-separated list of namespace names
- `--username`: Username for the workspace
- `--email`: Email address for the workspace

### 2. create_workspace_with_auto_gpr.py
Creates a workspace with automatic GPR (GPU Request) functionality enabled.

**Usage:**
```bash
python create_workspace_with_auto_gpr.py --config workspace_config.yaml
```

**Arguments:**
- `--config`: Path to YAML configuration file

**Workflow:**
1. Creates workspace from YAML config
2. Downloads kubeconfigs for all clusters
3. Creates GPR templates for each cluster
4. Creates single GPR template binding for all clusters
5. Creates workspace-specific API keys

### 3. delete_workspace.py
Deletes a workspace and cleans up associated resources.

**Usage:**
```bash
python delete_workspace.py --config workspace_config.yaml
```

**Arguments:**
- `--config`: Path to YAML configuration file

### 4. download_kubeconfig.py
Downloads kubeconfig files for specific clusters in a workspace.

**Usage:**
```bash
python download_kubeconfig.py --workspace "tezz-slice" --cluster "worker-1"
```

**Arguments:**
- `--workspace`: Name of the workspace
- `--cluster`: Name of the cluster
- `--output_dir`: Output directory (optional, defaults to script location)

## Common Parameters

- `--workspace_name`: Name of the workspace to create
- `--clusters`: Comma-separated list of cluster names
- `--namespaces`: Comma-separated list of namespace names
- `--username`: Username for the workspace
- `--email`: Email address for the workspace
- `--config`: Path to YAML configuration file

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
