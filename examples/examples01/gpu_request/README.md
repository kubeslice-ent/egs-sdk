# GPU Request (GPR) Scripts

This folder contains scripts for managing GPU Requests (GPRs) using the EGS SDK.

## Environment Variables Required

- `EGS_ENDPOINT`: EGS API endpoint (required)
- `EGS_API_KEY`: EGS API key for authentication (required)

## Common Parameters

- `--request_name`: Name of the GPU request
- `--workspace_name`: Name of the workspace
- `--priority`: Priority of the request (lower number = higher priority)
- `--memory_per_gpu`: Memory per GPU in GB
- `--exit_duration`: Exit duration (e.g., '1h', '30m')
- `--node_count`: Number of nodes (default: 1)
- `--gpu_per_node_count`: Number of GPUs per node (default: 1)

## Selection Strategies

1. **Auto GPU + Auto Cluster**: System automatically selects best GPU type and cluster
2. **Auto GPU + Manual Cluster**: System selects GPU type, user specifies preferred clusters
3. **Auto Cluster + Manual GPU**: System selects cluster, user specifies GPU instance type and shape
4. **Manual GPU + Manual Cluster**: User specifies both GPU type and cluster

## Scripts Overview

### 1. make_gpr_with_auto_selection.py
Creates a GPR with both auto GPU and auto cluster selection enabled.

**Usage:**
```bash
python make_gpr_with_auto_selection.py --request_name "demo-auto" --workspace_name "tezz-slice" --priority 100 --memory_per_gpu 22 --exit_duration "1h"
```

**Arguments:**
- `--request_name`: Name of the GPU request
- `--workspace_name`: Name of the workspace
- `--priority`: Priority of the request
- `--memory_per_gpu`: Memory per GPU in GB
- `--exit_duration`: Exit duration

### 2. make_gpr_with_auto_gpu.py
Creates a GPR with auto GPU selection and manual cluster selection.

**Usage:**
```bash
python make_gpr_with_auto_gpu.py --request_name "demo-auto-gpu" --workspace_name "tezz-slice" --priority 100 --memory_per_gpu 22 --exit_duration "1h" --preferred_clusters "worker-1,worker-2"
```

**Arguments:**
- `--request_name`: Name of the GPU request
- `--workspace_name`: Name of the workspace
- `--priority`: Priority of the request
- `--memory_per_gpu`: Memory per GPU in GB
- `--exit_duration`: Exit duration
- `--preferred_clusters`: Comma-separated list of preferred cluster names

### 3. make_gpr_with_auto_cluster.py
Creates a GPR with auto cluster selection and manual GPU selection.

**Usage:**
```bash
python make_gpr_with_auto_cluster.py --request_name "demo-auto-cluster" --workspace_name "tezz-slice" --priority 100 --memory_per_gpu 22 --exit_duration "1h" --instance_type "VM.GPU.A10.2" --gpu_shape "NVIDIA-A10"
```

**Arguments:**
- `--request_name`: Name of the GPU request
- `--workspace_name`: Name of the workspace
- `--priority`: Priority of the request
- `--memory_per_gpu`: Memory per GPU in GB
- `--exit_duration`: Exit duration
- `--instance_type`: GPU instance type (e.g., "VM.GPU.A10.2")
- `--gpu_shape`: GPU shape (e.g., "NVIDIA-A10")

### 4. make_gpr_with_manual_selection.py
Creates a GPR with both auto GPU and auto cluster selection disabled (manual selection).

**Usage:**
```bash
python make_gpr_with_manual_selection.py --request_name "demo-manual" --workspace_name "tezz-slice" --priority 100 --memory_per_gpu 22 --exit_duration "1h" --cluster_name "worker-1" --instance_type "VM.GPU.A10.2" --gpu_shape "NVIDIA-A10"
```

**Arguments:**
- `--request_name`: Name of the GPU request
- `--workspace_name`: Name of the workspace
- `--priority`: Priority of the request
- `--memory_per_gpu`: Memory per GPU in GB
- `--exit_duration`: Exit duration
- `--cluster_name`: Specific cluster name
- `--instance_type`: GPU instance type
- `--gpu_shape`: GPU shape

### 5. make_gpr.py
General-purpose GPR creation script with flexible selection options.

**Usage:**
```bash
python make_gpr.py --request_name "demo" --workspace_name "tezz-slice" --priority 100 --memory_per_gpu 22 --exit_duration "1h" --enable_auto_gpu_selection --enable_auto_cluster_selection
```

**Arguments:**
- `--request_name`: Name of the GPU request
- `--workspace_name`: Name of the workspace
- `--priority`: Priority of the request
- `--memory_per_gpu`: Memory per GPU in GB
- `--exit_duration`: Exit duration
- `--enable_auto_gpu_selection`: Enable automatic GPU selection
- `--enable_auto_cluster_selection`: Enable automatic cluster selection

### 6. list_gprs.py
Lists all GPU Requests (GPRs) for a specific workspace in table format.

**Usage:**
```bash
python list_gprs.py --workspace "tezz-slice"
```

**Arguments:**
- `--workspace`: Name of the workspace to list GPRs for

**Output Format:**
- GPR Name, ID, Cluster, Status
- Total GPUs, Instance Type, GPU Shape, Priority

### 7. release_gpr.py
Releases or cancels a GPU Request based on its current status.

**Usage:**
```bash
python release_gpr.py --request_id "gpr-12345"
```

**Arguments:**
- `--request_id`: ID of the GPR to release/cancel

**Behavior:**
- If status is "Queued" or "Pending" → Cancels the request
- If status is "Complete" → Shows "GPR is already Completed"
- Otherwise → Releases the GPU request

## Output

- **make_gpr_*.py**: Creates GPR and returns GPR ID
- **list_gprs.py**: Displays GPRs in a formatted table
- **release_gpr.py**: Returns success/failure message based on operation
