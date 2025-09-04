# Workspace Policy Management Scripts

This folder contains scripts for managing workspace policies using the EGS SDK.

## Environment Variables Required

- `EGS_ENDPOINT`: EGS API endpoint (required)
- `EGS_API_KEY`: EGS API key for authentication (required)

## Scripts Overview

### 1. list_workspace_policies.py
Lists all workspace policies in the system.

**Usage:**
```bash
python list_workspace_policies.py
```



### 2. get_workspace_policy.py
Gets a specific workspace policy by workspace name.

**Usage:**
```bash
python get_workspace_policy.py --policy-name "my-workspace"
```

**Arguments:**
- `--policy-name`: Name of the workspace to get policy for (required)



### 3. update_workspace_policy.py
Updates a workspace policy with new configuration.

**Usage:**
```bash
# Update priority range and max GPRs
python update_workspace_policy.py --policy-name "my-workspace" --priority-range "high" --max-gprs 5

# Update GPU constraints
python update_workspace_policy.py --policy-name "my-workspace" --gpu-shapes "NVIDIA-A10,Tesla-P100" --max-gpu-per-gpr 2

# Update multiple parameters
python update_workspace_policy.py --policy-name "my-workspace" --priority-range "medium" --max-gprs 3 --enable-auto-eviction
```

**Arguments:**
- `--policy-name`: Name of the workspace to update policy for (required)
- `--priority-range`: Priority range ("high", "medium", "low")
- `--max-gprs`: Maximum number of GPRs allowed
- `--max-exit-duration`: Maximum exit duration per GPR (e.g., "1h", "30m", "1d")
- `--enforce-idle-timeout`: Enable idle timeout enforcement
- `--requeue-on-failure`: Enable requeue on failure
- `--enable-auto-eviction`: Enable auto eviction
- `--gpu-shapes`: Comma-separated list of allowed GPU shapes
- `--max-gpu-per-gpr`: Maximum GPUs per GPR
- `--max-memory-per-gpr`: Maximum memory per GPR in GB

## Example Usage

### List All Policies
```bash
python list_workspace_policies.py
```

### Get Specific Policy
```bash
python get_workspace_policy.py --policy-name "color"
```

### Update Policy for High-Performance Workloads
```bash
python update_workspace_policy.py \
  --policy-name "high-perf-workspace" \
  --priority-range "high" \
  --max-gprs 10 \
  --gpu-shapes "NVIDIA-A10,Tesla-V100" \
  --max-gpu-per-gpr 4 \
  --max-memory-per-gpr 32
```

### Update Policy for Development Environment
```bash
python update_workspace_policy.py \
  --policy-name "dev-workspace" \
  --priority-range "low" \
  --max-gprs 2 \
  --max-exit-duration "2h" \
  --enable-auto-eviction
```

## Error Handling

All scripts include comprehensive error handling:

- **ResourceNotFound**: When workspace policy doesn't exist
- **BadParameters**: When invalid parameters are provided
- **UnhandledException**: For unexpected API errors
- **EnvironmentError**: When required environment variables are missing

## Output

- **list_workspace_policies.py**: Displays all policies in formatted table
- **get_workspace_policy.py**: Shows detailed policy information
- **update_workspace_policy.py**: Displays updated policy configuration

### Example Table Output

```
Listing all workspace policies...
Found 3 workspace policies:
========================================================================================================================
Workspace            Priority   Max GPRs   Max Duration    Requeue Auto Evict GPU Shapes           Max GPU Max Memory
------------------------------------------------------------------------------------------------------------------------
my-workspace         high       5          2h              true    true        NVIDIA-A10, NVIDIA.. 4       22GB
test-workspace       medium     3          1h              false   true        *                    2       15GB
demo-workspace       low        2          30m             true    false       N/A                  N/A     N/A
```

**Note**: Long values are truncated with ".." to maintain table formatting.

