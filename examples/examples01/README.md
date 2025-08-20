
# EGS SDK Examples

This folder contains comprehensive examples for using the EGS SDK to manage workspaces, GPU requests, inventory, and workload deployments.

## Environment Variables Required

- `EGS_ENDPOINT`: EGS API endpoint (required)
- `EGS_API_KEY`: EGS API key for authentication (required)

## Prerequisites

### Python Version
Ensure you have Python version 3.9 or later installed on your system.

### Install the Required Python Package
```bash
pip install git+https://github.com/kubeslice-ent/egs-sdk.git
```

If you want to install a specific branch or version, specify the branch as in the following command:
```bash
pip install git+https://github.com/kubeslice-ent/egs-sdk.git@<branch_or_tag_name>
```

## Folder Structure

- **`workspace/`**: Workspace management scripts (create, delete, kubeconfig download)
- **`gpu_request/`**: GPU Request (GPR) management scripts (create, list, release)
- **`inventory/`**: Inventory listing and GPU information scripts
- **`workload_deployment/`**: Kubernetes workload deployment scripts and manifests

## Workspace Management

### Workspace Configuration YAML

The workspace scripts use a configuration file in YAML format.

**Structure:**
```yaml
projectname: "avesha"
workspaces:
  - name: "workspace-b"
    namespaces:
      - "namespace-b2"
      - "namespace-b1"
    clusters:
      - "worker-1"
      # - "worker-2" (Optional additional cluster)
    username: "admin-1"
    email: "admin1@acme.io"
```

**Required Fields:**
- `projectname`: The project name associated with the workspaces
- `workspaces`: A list of workspace configurations
- `name`: The name of the workspace
- `namespaces`: List of namespaces associated with the workspace
- `clusters`: List of clusters to associate with the workspace
- `username`: The username associated with the workspace
- `email`: The contact email for the workspace

### Available Scripts

**See:** `workspace/README.md` for detailed documentation of all workspace scripts.

## GPU Request (GPR) Management

### Create a GPR
The `make_gpr.py` script is used to create a GPR.

**Basic Syntax:**
```bash
python make_gpr.py --cluster_name <cluster-name> --workspace_name <workspace-name> --priority <priority-number> --exit_duration <duration-in-0d0h0m> --request_name <gpr-request-name> --gpu_shape <GPU shape>
```

**Examples:**

**With GPU shape parameter:**
```bash
python make_gpr.py --cluster_name "worker-1" --workspace_name test1 --priority 100 --exit_duration 5m --request_name test-gpr4 --gpu_shape Tesla-P100-PCIE-16GB
```

**Without GPU shape parameter (defaults to first node, first GPU):**
```bash
python make_gpr.py --cluster_name "worker-1" --workspace_name test1 --priority 100 --exit_duration 5m --request_name test-gpr1
```

### Release a GPR
The `release_gpr.py` script is used to release a GPR.

**Syntax:**
```bash
python release_gpr.py --request_id <gpr-request-id>
```

**Example:**
```bash
python release_gpr.py --request_id gpr-191b3dd5-f110
```

**Behavior:**
- If status is "Queued" → Cancels the request
- If status is "Successful" → Releases the GPU request

### Available Scripts

**See:** `gpu_request/README.md` for detailed documentation of all GPR scripts.

## Inventory Management

### List Inventory
Scripts to view and analyze GPU inventory across clusters.

**See:** `inventory/README.md` for detailed documentation of inventory scripts.

## Workload Deployment

### GPU Workload Deployment
The `workload_deployment/` folder contains scripts and manifests for deploying GPU workloads on EGS clusters.

**Main Script:** `workload_deployment/deploy_gpu_workload.py`

**Usage:**
```bash
python workload_deployment/deploy_gpu_workload.py --workspace "tezz-slice" --cluster "worker-1" --manifest "workload_deployment/deploy.yaml" --namespace "default"
```

**Required Arguments:**
- `--workspace`: Workspace name
- `--cluster`: Cluster name  
- `--manifest`: Path to deployment YAML manifest file
- `--namespace`: Namespace for deployment (must be onboarded into the workspace)

**Example:**
```bash
python workload_deployment/deploy_gpu_workload.py --workspace "test1" --cluster "worker-1" --manifest "workload_deployment/deploy.yaml" --namespace "default"
```

**See:** `workload_deployment/README.md` for detailed documentation.

## Common Parameters

- `--workspace_name` / `--workspace`: Name of the workspace
- `--cluster_name` / `--cluster`: Name of the cluster
- `--priority`: Priority of the request (lower number = higher priority)
- `--exit_duration`: Exit duration (e.g., '5m', '1h', '0d0h0m')
- `--request_name`: Name of the GPU request
- `--gpu_shape`: GPU shape specification (optional)

## Output

On successful execution, scripts will:

* Create workspaces and save kubeconfig files in `kubeconfigs/<workspace_name>/`
* Retrieve and save Kubernetes authentication tokens as `token.txt`
* Log messages indicating success or failure for each step
* Return GPR IDs for GPU requests
* Deploy workloads to specified clusters

## Troubleshooting

If you encounter issues:

* Verify that the correct EGS API credentials are being used
* Check for proper formatting of YAML configuration files
* Review error messages to identify missing dependencies or incorrect configurations
* Ensure all required environment variables are set
