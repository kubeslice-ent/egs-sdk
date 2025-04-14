# GPR Template SDK Usage 📘

This document describes how to use the Python SDK to interact with the GPR Template APIs, including creation, retrieval, listing, updating, and deletion of GPU provisioning templates.

---

## `create_gpr_template`

Creates a new GPR template.

```python
from egs.gpr_template import create_gpr_template

create_gpr_template(
    name="my-template",
    cluster_name="worker-cluster",
    gpu_per_node_count=1,
    num_gpu_nodes=2,
    memory_per_gpu=40,
    gpu_shape="A100",
    instance_type="a2-highgpu-2g",
    exit_duration="1h",
    priority=100,
    enforce_idle_timeout=True,
    idle_timeout_duration="10m",
    enable_eviction=True,
    requeue_on_failure=False
)
```

### 📥 Parameters

| Parameter               | Type      | Description |
|-------------------------|-----------|-------------|
| `name`                 | `str`     | Name of the GPR template. |
| `cluster_name`         | `str`     | Name of the target cluster. |
| `gpu_per_node_count`   | `int`     | Number of GPUs per node. |
| `num_gpu_nodes`        | `int`     | Total number of GPU nodes. |
| `memory_per_gpu`       | `int`     | Memory (in GB) per GPU. |
| `gpu_shape`            | `str`     | Type/model of GPU (e.g., A100). |
| `instance_type`        | `str`     | Cloud VM type (e.g., a2-highgpu-2g). |
| `exit_duration`        | `str`     | Duration before graceful exit (e.g., 1h). |
| `priority`             | `int`     | Scheduling priority of the job. |
| `enforce_idle_timeout` | `bool`    | Whether idle timeout logic is active. |
| `idle_timeout_duration`| `str`     | Idle timeout period (if enforced). |
| `enable_eviction`      | `bool`    | Whether idle jobs can be evicted. |
| `requeue_on_failure`   | `bool`    | Whether failed jobs should be requeued. |
| `authenticated_session`| `Optional[AuthenticatedSession]` | Optional auth session. |

**Returns**: `str` (template name)

---

## `get_gpr_template`

Fetches a GPR template by name.

```python
from egs.gpr_template import get_gpr_template

template = get_gpr_template("my-template")
print(template.name)
```

### 📥 Parameters

| Parameter             | Type   | Description |
|-----------------------|--------|-------------|
| `gpr_template_name`   | `str`  | Name of the GPR template. |
| `authenticated_session` | `Optional[AuthenticatedSession]` | Optional auth session. |

**Returns**: `GetGprTemplateResponse`

---

## `list_gpr_templates`

Lists all GPR templates.

```python
from egs.gpr_template import list_gpr_templates

templates = list_gpr_templates()
for t in templates.items:
    print(t.name)
```

### 📥 Parameters

| Parameter               | Type   | Description |
|-------------------------|--------|-------------|
| `authenticated_session` | `Optional[AuthenticatedSession]` | Optional auth session. |

**Returns**: `ListGprTemplatesResponse`

---

## `update_gpr_template`

Updates an existing GPR template.

```python
from egs.gpr_template import update_gpr_template

update_gpr_template(
    name="my-template",
    cluster_name="worker-cluster",
    number_of_gpus=2,
    number_of_gpu_nodes=2,
    memory_per_gpu=40,
    gpu_shape="A100",
    instance_type="a2-highgpu-2g",
    exit_duration="2h",
    priority=120,
    enforce_idle_timeout=True,
    idle_timeout_duration="15m",
    enable_eviction=True,
    requeue_on_failure=True
)
```

### 📥 Parameters

| Parameter               | Type      | Description |
|-------------------------|-----------|-------------|
| `name`                 | `str`     | Template name. |
| `cluster_name`         | `str`     | Name of the target cluster. |
| `number_of_gpus`       | `int`     | Total number of GPUs required. |
| `instance_type`        | `str`     | Instance type (e.g., a2-highgpu-2g). |
| `exit_duration`        | `str`     | Graceful exit duration (e.g., 2h). |
| `number_of_gpu_nodes`  | `int`     | Number of GPU nodes. |
| `priority`             | `int`     | Job scheduling priority. |
| `memory_per_gpu`       | `int`     | Memory (in GB) per GPU. |
| `gpu_shape`            | `str`     | GPU shape/model. |
| `enable_eviction`      | `bool`    | Eviction toggle. |
| `requeue_on_failure`   | `bool`    | Retry failed jobs. |
| `enforce_idle_timeout` | `bool`    | Whether to enforce idle time. |
| `idle_timeout_duration`| `str`     | Idle timeout duration if enabled. |
| `authenticated_session`| `Optional[AuthenticatedSession]` | Auth session (optional). |

**Returns**: `UpdateGprTemplateResponse`

---

## `delete_gpr_template`

Deletes a GPR template by name.

```python
from egs.gpr_template import delete_gpr_template

delete_gpr_template("my-template")
```

### 📥 Parameters

| Parameter               | Type   | Description |
|-------------------------|--------|-------------|
| `gpr_template_name`     | `str`  | Template name to delete. |
| `authenticated_session` | `Optional[AuthenticatedSession]` | Optional auth session. |

**Returns**: `DeleteGprTemplateResponse`

---
