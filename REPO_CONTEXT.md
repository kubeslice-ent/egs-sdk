# REPO_CONTEXT: egs-sdk

## Purpose
Python SDK for the Elastic GPU Service (EGS). Provides a programmatic interface for submitting GPU Provisioning Requests (GPRs), managing inference endpoints, querying wait times, and releasing GPU resources — abstracting away the REST API calls to `egs-core-apis`.

## Role in EGS System
Primary developer-facing interface for EGS. Data scientists and ML engineers use this SDK to:
- Request GPU allocations for training or inference jobs
- Poll for GPR status and wait-time estimates
- Release GPUs early when workloads complete
- Manage inference endpoint lifecycle

## Tech Stack
- **Language:** Python 3.8+
- **Package:** `egs` (installed via `pip install -e .` or `pip install egs`)
- **Key dependencies:** `requests`, `kubernetes` (Python client)

## Key Components
```
egs/                    - Main package
  gpr.py                - GPR lifecycle: create, get, update, delete, wait_for_ready
  inference.py          - Inference endpoint management
  client.py             - HTTP client wrapper for egs-core-apis REST calls
  config.py             - SDK configuration (API URL, auth token, cluster name)
examples/               - Runnable usage examples
  submit_gpr.py
  inference_endpoint.py
docs/                   - API reference documentation
setup.py                - Package metadata and dependencies
CHANGELOG.md            - Version history
```

## Usage
```python
from egs import EGSClient

client = EGSClient(api_url="https://egs.example.com", token="<token>")

# Submit a GPU request
gpr = client.create_gpr(
    name="my-training-job",
    cluster="gpu-cluster-1",
    instance_type="p3.8xlarge",
    num_gpus=4,
    priority=50
)

# Wait for allocation
gpr.wait_for_ready(timeout=600)

# Release early
gpr.release()
```

## Dependencies & Integrations
- **egs-core-apis** — all SDK calls go to this REST API
- **egs-sdk-scripts** — higher-level workflow scripts built on top of this SDK
- **egs-sdk-test-framework** — integration test framework for validating SDK behavior
