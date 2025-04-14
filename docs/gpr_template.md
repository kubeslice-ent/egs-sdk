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

**Parameters**:
- `name`, `cluster_name`, `gpu_per_node_count`, `num_gpu_nodes`, `memory_per_gpu`, `gpu_shape`, `instance_type`, `exit_duration`, `priority`
- `enforce_idle_timeout`, `idle_timeout_duration`, `enable_eviction`, `requeue_on_failure`

**Returns**: `str` (template name)

---

## `get_gpr_template`

Fetches a GPR template by name.

```python
from egs.gpr_template import get_gpr_template

template = get_gpr_template("my-template")
print(template.name)
```

**Parameters**:
- `gpr_template_name`: Name of the GPR template

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

**Returns**: `UpdateGprTemplateResponse`

---

## `delete_gpr_template`

Deletes a GPR template by name.

```python
from egs.gpr_template import delete_gpr_template

delete_gpr_template("my-template")
```

**Returns**: `DeleteGprTemplateResponse`

---

## 🔗 Reference from Main README

To reference this doc, add this line to your README.md:

```markdown
## GPR Template APIs 📦

For full usage instructions, visit the [GPR Template SDK Documentation](docs/gpr_template.md).
```

---