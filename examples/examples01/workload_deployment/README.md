# GPU Workload Deployment

This folder contains scripts and manifests for deploying GPU workloads on EGS clusters.

## Files

### 1. deploy_gpu_workload.py
Main script to download kubeconfig and deploy GPU workloads from YAML manifests.

**Usage:**
```bash
python deploy_gpu_workload.py \
  --workspace "your-workspace" \
  --cluster "your-cluster" \
  --manifest "deploy.yaml" \
  --namespace "your-namespace"
```

**Features:**
- Downloads kubeconfig for the specified workspace and cluster
- Creates GPR (GPU Request) with auto GPU selection and manual cluster selection
- Initializes Kubernetes client using the downloaded kubeconfig
- Loads deployment manifest from YAML file
- Creates deployment with proper resource configuration
- Supports any Kubernetes deployment manifest

**Required Arguments:**
- `--workspace`: Workspace name
- `--cluster`: Cluster name  
- `--manifest`: Path to deployment YAML manifest file
- `--namespace`: Namespace for deployment (must be onboarded into the workspace)

**Optional Arguments:**
- `--output-dir`: Output directory for kubeconfig files (default: script directory)

### 2. deploy.yaml
Sample Kubernetes deployment manifest for GPU workloads.

**Features:**
- Generic deployment template that can be customized
- GPU resource requests and limits
- Health checks (liveness and readiness probes)
- Service definition for networking
- Configurable environment variables

## Workflow

1. **Authentication**: Script authenticates with EGS using environment variables
2. **Kubeconfig Download**: Downloads cluster kubeconfig for the specified workspace
3. **Manifest Loading**: Loads and validates the deployment YAML manifest
4. **Kubernetes Client**: Initializes Kubernetes client using the downloaded kubeconfig
5. **GPR Creation**: Creates GPU Request with specified parameters
6. **Deployment**: Deploys the workload to the cluster

## Environment Variables

Ensure these are set before running:
```bash
export EGS_ENDPOINT="your-egs-endpoint"
export EGS_API_KEY="your-egs-api-key"
```

## GPR Configuration

The script creates a GPR with these default settings:
- **Memory per GPU**: 22GB
- **Exit Duration**: 1 hour
- **Priority**: 250
- **Idle Timeout**: 30 minutes
- **Auto GPU Selection**: Enabled
- **Manual Cluster Selection**: Uses specified cluster

## Example Usage

```bash
# Deploy to default namespace
python deploy_gpu_workload.py \
  --workspace "tezz-slice" \
  --cluster "worker-1" \
  --manifest "deploy.yaml" \
  --namespace "default"

# Deploy to custom namespace
python deploy_gpu_workload.py \
  --workspace "my-workspace" \
  --cluster "worker-1" \
  --manifest "deploy.yaml" \
  --namespace "my-namespace"
```
