# Update Workspace Script

The `update_workspace.py` script allows you to add new namespaces and clusters to existing workspaces using the EGS SDK.

## Features

1. **Add namespaces to existing workspaces**
2. **Add clusters to existing workspaces**
3. **Batch updates from configuration files**
4. **Single workspace updates via command line**
5. **Automatic kubeconfig generation for new clusters**

## Prerequisites

- Environment variables: `EGS_ENDPOINT` and either `EGS_API_KEY` or `EGS_ACCESS_TOKEN`
- Python dependencies: `egs`, `yaml`, `kubernetes`
- Existing workspaces to update

## Usage

### Method 1: Batch Updates from Configuration File

Create a YAML configuration file (e.g., `update_workspace_config.yaml`):

```yaml
projectname: "avesha"
workspaces:
  - name: "workspace-3a"
    add_namespaces:
      - "namespace-3a3"
      - "namespace-3a4"
    add_clusters:
      - "worker-2"
      - "worker-3"
```

Run the script:

```bash
python update_workspace.py --config update_workspace_config.yaml
```

### Method 2: Single Workspace Updates via Command Line

Add a namespace to a specific workspace:

```bash
python update_workspace.py --config update_workspace_config.yaml --workspace "workspace-3a" --add-namespace "new-namespace"
```

Add a cluster to a specific workspace:

```bash
python update_workspace.py --config update_workspace_config.yaml --workspace "workspace-3a" --add-cluster "new-cluster"
```

Add both namespace and cluster:

```bash
python update_workspace.py --config update_workspace_config.yaml --workspace "workspace-3a" --add-namespace "new-namespace" --add-cluster "new-cluster"
```

## Configuration File Format

The configuration file follows this structure:

```yaml
projectname: "your-project-name"
workspaces:
  - name: "workspace-name"
    add_namespaces: # Optional: List of namespaces to add
      - "namespace-1"
      - "namespace-2"
    add_clusters: # Optional: List of clusters to add
      - "cluster-1"
      - "cluster-2"
```

## Key Functions

### `add_namespace_to_workspace(workspace_name, namespace, auth)`

- Adds a new namespace to an existing workspace
- Includes fallback logic for different EGS SDK versions
- Prevents duplicate namespace additions

### `add_cluster_to_workspace(workspace_name, cluster_name, auth)`

- Adds a new cluster to an existing workspace
- Automatically generates and saves kubeconfig files
- Creates kubeconfig directory structure
- Prevents duplicate cluster additions

## Output

The script will:

1. Authenticate using your API key or access token
2. Process each workspace in the configuration file
3. Add specified namespaces and clusters
4. Generate kubeconfig files for new clusters
5. Provide status updates and error handling

## Error Handling

- **Duplicate Prevention**: Checks for existing namespaces/clusters before adding
- **Graceful Failures**: Continues processing other items if one fails
- **Detailed Logging**: Provides clear success/failure messages
- **Exception Handling**: Catches and reports various error types

## File Structure After Running

```
kubeconfigs/
└── workspace-name/
    ├── cluster-1.config
    ├── cluster-2.config
    └── apikey.txt
```

## Environment Variables

Required environment variables:

- `EGS_ENDPOINT`: The EGS API endpoint URL
- `EGS_API_KEY` OR `EGS_ACCESS_TOKEN`: Authentication credentials

## Examples

See `update_workspace_config.yaml` for a complete example configuration file.

## Notes

- The script includes fallback mechanisms for different EGS SDK API versions
- Small delays are added between operations to avoid rate limiting
- Kubeconfig files are automatically generated and saved for new clusters
- The script follows the same authentication pattern as `create_workspace.py` and `delete_workspace.py`
