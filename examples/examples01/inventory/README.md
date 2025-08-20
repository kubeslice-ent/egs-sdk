# Inventory Management Scripts

This folder contains scripts for viewing and analyzing GPU inventory across EGS clusters.

## Environment Variables Required

- `EGS_ENDPOINT`: EGS API endpoint (required)
- `EGS_API_KEY`: EGS API key for authentication (required)

## Common Parameters

- No command-line arguments required - shows all inventory by default
- Displays comprehensive GPU information in table format
- Automatically fetches inventory from all available clusters

## Scripts Overview

### 1. list_inventory.py
Lists all GPU inventory across clusters in a formatted table.

**Usage:**
```bash
python list_inventory.py
```

**Output Format:**
- **Node Name**: Name of the GPU node (truncated if >20 characters)
- **Cluster**: Cluster name where the node is located
- **GPU Shape**: Type of GPU (e.g., NVIDIA-A10, Tesla-P100)
- **Instance Type**: VM instance type (e.g., VM.GPU.A10.2)
- **Memory (GB)**: Available memory in GB
- **Total GPUs**: Total number of GPUs on the node
- **Available**: Number of available GPUs
- **Status**: Current status of the GPU node

**Table Structure:**
```
========================================================================================================================
Node Name            Cluster         GPU Shape        Instance Type        Memory (GB) Total GPUs Available Status      
========================================================================================================================
worker-1-node-001    worker-1        NVIDIA-A10       VM.GPU.A10.2        22          2         1         Running      
worker-2-node-002    worker-2        Tesla-P100       VM.GPU.P100.1       16          1         0         Running      
========================================================================================================================
```

## Data Sources

The script uses the EGS SDK's `inventory()` function to fetch:
- Node information across all clusters
- GPU specifications and availability
- Memory and resource details
- Current status of GPU nodes

## Output

- **Formatted Table**: Easy-to-read inventory display
- **Truncated Names**: Long names are shortened with "..." for table formatting
- **Cluster Information**: Shows which cluster each node belongs to
- **Resource Details**: Comprehensive GPU and memory information
- **Status Information**: Current operational status of nodes

## Troubleshooting

If you encounter issues:

* Ensure all required environment variables are set
* Verify EGS API connectivity
* Check that you have proper permissions to view inventory
* Ensure the EGS endpoint is accessible
* Verify the API key has inventory read permissions

## Example Output

```bash
$ python list_inventory.py

========================================================================================================================
Node Name            Cluster         GPU Shape        Instance Type        Memory (GB) Total GPUs Available Status      
========================================================================================================================
worker-1-node-001    worker-1        NVIDIA-A10       VM.GPU.A10.2        22          2         1         Running      
worker-1-node-002    worker-1        NVIDIA-A10       VM.GPU.A10.2        22          2         2         Running      
worker-2-node-001    worker-2        Tesla-P100       VM.GPU.P100.1       16          1         0         Running      
========================================================================================================================

Total nodes found: 3
```
