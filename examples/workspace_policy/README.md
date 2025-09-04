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
python examples/workspace_policy/list_workspace_policies.py
```



### 2. get_workspace_policy.py
Gets a specific workspace policy by workspace name.

**Usage:**
```bash
python examples/workspace_policy/get_workspace_policy.py --policy-name "my-workspace"
```

**Arguments:**
- `--policy-name`: Name of the workspace to get policy for (required)



### 3. update_workspace_policy.py
Updates a workspace policy with new configuration.

**Usage:**
```bash
python examples/workspace_policy/update_workspace_policy.py \
  --policy-name "tezz-slice" \
  --priority-range "high" \
  --max-gprs 5 \
  --gpu-shapes "NVIDIA-A10" \
  --max-gpu-per-gpr 2

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

## Error Handling

All scripts include comprehensive error handling:

- **ResourceNotFound**: When workspace policy doesn't exist
- **BadParameters**: When invalid parameters are provided
- **UnhandledException**: For unexpected API errors
- **EnvironmentError**: When required environment variables are missing
