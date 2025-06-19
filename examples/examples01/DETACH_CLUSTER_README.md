# Detach Cluster from Workspace/Slice

The `detach_cluster_from_workspace.py` script allows you to detach clusters from existing workspaces (slices) using the EGS SDK. This functionality is similar to `createworkspace` and `updateworkspace`, but specifically focused on removing cluster attachments from slices.

## 🚀 Features

1. **Detach clusters from existing workspaces/slices**
2. **Attach clusters to workspaces (for testing purposes)**
3. **Batch detach operations from configuration files**
4. **Single workspace operations via command line**
5. **Detailed workspace information display**
6. **Safety checks to prevent invalid operations**

## 📋 Prerequisites

- Environment variables: `EGS_ENDPOINT` and either `EGS_API_KEY` or `EGS_ACCESS_TOKEN`
- Python dependencies: `egs`, `yaml`
- Existing workspaces with multiple clusters (cannot detach the last cluster)

## 🔧 New SDK Functions

This implementation adds the following new functions to the EGS SDK:

### `egs.update_workspace()`

```python
egs.update_workspace(
    workspace_name="my-workspace",
    clusters=["cluster-1", "cluster-2"],  # Optional: None preserves existing
    namespaces=["ns-1", "ns-2"],          # Optional: None preserves existing
    authenticated_session=auth
)
```

### `egs.detach_cluster_from_workspace()`

```python
egs.detach_cluster_from_workspace(
    workspace_name="my-workspace",
    cluster_name="cluster-to-remove",
    authenticated_session=auth
)
```

## 📖 Usage

### Method 1: Single Workspace Operations

#### List all workspaces:

```bash
python detach_cluster_from_workspace.py --list
```

#### Show detailed workspace information:

```bash
python detach_cluster_from_workspace.py --workspace "my-workspace" --show-details
```

#### Detach a cluster from a workspace:

```bash
python detach_cluster_from_workspace.py --workspace "my-workspace" --detach-cluster "worker-2"
```

#### Attach a cluster to a workspace (for testing):

```bash
python detach_cluster_from_workspace.py --workspace "my-workspace" --attach-cluster "worker-3"
```

### Method 2: Batch Operations from Configuration File

Create a YAML configuration file (e.g., `detach_cluster_config.yaml`):

```yaml
projectname: "avesha"

detach_operations:
  - workspace_name: "workspace-3a"
    cluster_name: "worker-2"

  - workspace_name: "workspace-3b"
    cluster_name: "worker-3"
```

Run the batch operation:

```bash
python detach_cluster_from_workspace.py --config detach_cluster_config.yaml
```

## ⚠️ Safety Features

The implementation includes several safety checks:

1. **Last Cluster Protection**: Cannot detach the last cluster from a workspace
2. **Workspace Validation**: Verifies workspace exists before attempting operations
3. **Cluster Validation**: Checks if cluster is actually attached to the workspace
4. **Detailed Error Messages**: Provides clear feedback on what went wrong

## 🔄 How It Works

The detach functionality follows the same patterns as `createworkspace` and `updateworkspace`:

1. **Data Classes**: Uses `UpdateWorkspaceRequest` and `UpdateWorkspaceResponse` data classes
2. **API Endpoint**: Calls `PUT /api/v1/slice-workspace` (similar to how create uses `POST`)
3. **Error Handling**: Includes proper exception handling with meaningful error messages
4. **Authentication**: Uses the same authentication patterns as existing functions

## 🏗️ Implementation Details

### File Structure

```
egs/
├── workspace.py                          # Updated with new functions
├── internal/workspace/
│   └── update_workspace_data.py         # New data classes
examples/examples01/
├── detach_cluster_from_workspace.py     # Main script
├── detach_cluster_config.yaml           # Sample configuration
└── DETACH_CLUSTER_README.md             # This documentation
```

### Key Functions Added

1. **`update_workspace()`**: General workspace update function
2. **`detach_cluster_from_workspace()`**: Specific cluster detachment function
3. **`_get_workspace_details()`**: Helper function to retrieve workspace information

## 📝 Configuration File Format

```yaml
projectname: "your-project-name"

detach_operations:
  - workspace_name: "workspace-name"
    cluster_name: "cluster-to-detach"

  - workspace_name: "another-workspace"
    cluster_name: "another-cluster"
```

## 🔍 Example Output

```bash
$ python detach_cluster_from_workspace.py --workspace "test-workspace" --detach-cluster "worker-2"

🎯 Detaching cluster 'worker-2' from workspace 'test-workspace'

📋 Workspace Details: test-workspace
   🔧 Clusters: ['worker-1', 'worker-2', 'worker-3']
   📦 Namespaces: ['test-namespace']
   🌐 Overlay Network Mode: hub-spoke
   📝 Description: Test workspace
   🎯 Max Clusters: 5

🔍 Checking workspace 'test-workspace' for cluster 'worker-2'...
✅ Found workspace: test-workspace
   Current clusters: ['worker-1', 'worker-2', 'worker-3']
🔄 Detaching cluster 'worker-2' from workspace 'test-workspace'...
✅ Successfully detached cluster 'worker-2' from workspace 'test-workspace'
   Updated clusters: ['worker-1', 'worker-3']

==================================================

📋 Workspace Details: test-workspace
   🔧 Clusters: ['worker-1', 'worker-3']
   📦 Namespaces: ['test-namespace']
   🌐 Overlay Network Mode: hub-spoke
   📝 Description: Test workspace
   🎯 Max Clusters: 5

✅ Detach operation completed.
```

## 🚨 Error Scenarios

### Cannot detach last cluster:

```bash
⚠️  Cannot detach the last cluster from workspace 'my-workspace'. At least one cluster must remain.
```

### Cluster not found:

```bash
⚠️  Cluster 'non-existent-cluster' is not attached to workspace 'my-workspace'
```

### Workspace not found:

```bash
❌ Workspace 'non-existent-workspace' not found
```

## 🔗 Integration with Existing Code

This implementation seamlessly integrates with existing EGS SDK patterns:

- **Similar to `createworkspace`**: Uses same authentication and error handling patterns
- **Similar to `updateworkspace`**: Uses PUT method for updates (like GPR template bindings)
- **Compatible with existing examples**: Follows same configuration file and CLI argument patterns

## 🧪 Testing

You can test the functionality by:

1. **Listing workspaces**: Verify your workspaces and their current clusters
2. **Attaching a test cluster**: Use the `--attach-cluster` option to add a cluster for testing
3. **Detaching the test cluster**: Use the `--detach-cluster` option to remove it
4. **Batch operations**: Test with configuration files for multiple operations

## 📚 Related Examples

- `create_workspace.py` - Creating new workspaces
- `update_workspace.py` - Adding clusters/namespaces to workspaces
- `update_workspace_v2.py` - Workspace recreation approach
- `delete_workspace.py` - Deleting workspaces

The detach cluster functionality provides a safer, more granular approach to workspace management compared to the recreation method used in `update_workspace_v2.py`.
