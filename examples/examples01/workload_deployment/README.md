# GPU Workload Deployment

This folder contains scripts and manifests for deploying GPU workloads on EGS clusters.

## Environment Variables Required

- `EGS_ENDPOINT`: EGS API endpoint (required)
- `EGS_API_KEY`: EGS API key for authentication (required)

## Common Parameters

- `--workspace`: Workspace name
- `--cluster`: Cluster name  
- `--manifest`: Path to deployment YAML manifest file
- `--namespace`: Namespace for deployment (must be onboarded into the workspace)
- `--output-dir`: Output directory for kubeconfig files (optional, default: script directory)

## GPR Configuration

The script creates a GPR with these default settings:
- **Memory per GPU**: 22GB
- **Exit Duration**: 1 hour
- **Priority**: 250
- **Idle Timeout**: 30 minutes
- **Auto GPU Selection**: Enabled
- **Manual Cluster Selection**: Uses specified cluster

## Scripts Overview

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

**Arguments:**
- `--workspace`: Workspace name
- `--cluster`: Cluster name  
- `--manifest`: Path to deployment YAML manifest file
- `--namespace`: Namespace for deployment (must be onboarded into the workspace)
- `--output-dir`: Output directory for kubeconfig files (optional, default: script directory)

**Workflow:**
1. **Authentication**: Script authenticates with EGS using environment variables
2. **Kubeconfig Download**: Downloads cluster kubeconfig for the specified workspace
3. **GPR Creation**: Creates GPU Request with specified parameters
4. **Manifest Loading**: Loads and validates the deployment YAML manifest
5. **Kubernetes Client**: Initializes Kubernetes client using the downloaded kubeconfig
6. **Deployment**: Deploys the workload to the cluster

### 2. deploy.yaml
Sample Kubernetes deployment manifest for GPU workloads.

**Structure:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-gpu-deployment
  labels:
    app: nginx-gpu
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx-gpu
  template:
    metadata:
      labels:
        app: nginx-gpu
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            nvidia.com/gpu: 1
          limits:
            nvidia.com/gpu: 1
```

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

# Deploy with custom output directory
python deploy_gpu_workload.py \
  --workspace "test1" \
  --cluster "worker-1" \
  --manifest "deploy.yaml" \
  --namespace "default" \
  --output-dir "/tmp/kubeconfigs"
```

## Output

- **GPR ID**: Returns the created GPU Request ID
- **Deployment Name**: Returns the created deployment name
- **Kubeconfig Files**: Downloads and saves kubeconfig to specified directory
- **Status Messages**: Provides step-by-step progress updates

## Troubleshooting

If you encounter issues:

* Ensure all required environment variables are set
* Verify the workspace and cluster exist
* Check that the namespace is onboarded into the workspace
* Ensure the deployment manifest is valid YAML
* Verify the manifest contains a valid Deployment resource
* Check that the cluster has available GPU resources
