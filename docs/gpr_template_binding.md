# GPR Template Binding SDK Usage 📘

This document describes how to use the Python SDK to manage GPR Template Bindings including creation, listing, retrieval, updating, and deletion.

---

## `create_gpr_template_binding`

Creates a new GPR template binding.

```python
from egs.gpr_template_binding import create_gpr_template_binding

response = create_gpr_template_binding(
    workspace_name="example-slice",
    clusters=[
        {
            "clusterName": "cluster-1",
            "defaultTemplateName": "default-template",
            "templates": ["template-a", "template-b"]
        }
    ],
    enable_auto_gpr=True
)
```

### 📥 Parameters

| Parameter           | Type        | Description |
|---------------------|-------------|-------------|
| `workspace_name`    | `str`       | Name of the workspace or slice. |
| `clusters`          | `List[Dict]`| List of clusters, each containing `clusterName`, `defaultTemplateName`, and `templates`. |
| `enable_auto_gpr`   | `bool`      | Enable automatic GPR binding. |
| `authenticated_session` | `Optional[AuthenticatedSession]` | Optional authentication context. |

**Returns**: `CreateGprTemplateBindingResponse`

---

## `get_gpr_template_binding`

Fetches a GPR template binding by name.

```python
from egs.gpr_template_binding import get_gpr_template_binding

response = get_gpr_template_binding("binding-name")
```

### 📥 Parameters

| Parameter             | Type   | Description |
|-----------------------|--------|-------------|
| `binding_name`        | `str`  | Name of the GPR binding to fetch. |
| `authenticated_session` | `Optional[AuthenticatedSession]` | Optional authentication context. |

**Returns**: `GetGprTemplateBindingResponse`

---

## `list_gpr_template_bindings`

Lists all GPR template bindings.

```python
from egs.gpr_template_binding import list_gpr_template_bindings

response = list_gpr_template_bindings()
```

### 📥 Parameters

| Parameter               | Type   | Description |
|-------------------------|--------|-------------|
| `authenticated_session` | `Optional[AuthenticatedSession]` | Optional authentication context. |

**Returns**: `ListGprTemplateBindingsResponse`

---

## `update_gpr_template_binding`

Updates an existing GPR template binding.

```python
from egs.gpr_template_binding import update_gpr_template_binding

response = update_gpr_template_binding(
    workspace_name="example-slice",
    clusters=[
        {
            "clusterName": "cluster-1",
            "defaultTemplateName": "updated-template",
            "templates": ["template-a", "template-c"]
        }
    ],
    enable_auto_gpr=False
)
```

### 📥 Parameters

| Parameter           | Type        | Description |
|---------------------|-------------|-------------|
| `workspace_name`    | `str`       | Name of the workspace or slice. |
| `clusters`          | `List[Dict]`| List of clusters, each containing `clusterName`, `defaultTemplateName`, and `templates`. |
| `enable_auto_gpr`   | `bool`      | Enable automatic GPR binding. |
| `authenticated_session` | `Optional[AuthenticatedSession]` | Optional authentication context. |

**Returns**: `UpdateGprTemplateBindingResponse`

---

## `delete_gpr_template_binding`

Deletes a GPR template binding by name.

```python
from egs.gpr_template_binding import delete_gpr_template_binding

response = delete_gpr_template_binding("binding-name")
```

### 📥 Parameters

| Parameter             | Type   | Description |
|-----------------------|--------|-------------|
| `binding_name`        | `str`  | Name of the GPR binding to delete. |
| `authenticated_session` | `Optional[AuthenticatedSession]` | Optional authentication context. |

**Returns**: `DeleteGprTemplateBindingResponse`

---
