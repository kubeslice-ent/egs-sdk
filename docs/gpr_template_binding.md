# GPR Template Binding SDK Usage 📘

These APIs allow interaction with GPR Template Bindings including creation, retrieval, listing, updating, and deletion.

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

**Parameters**:
- `workspace_name` (`str`): Slice name to bind templates.
- `clusters` (`List[Dict]`): Cluster configurations.
- `enable_auto_gpr` (`bool`): Toggle for auto GPR binding.

**Returns**: `CreateGprTemplateBindingResponse` object.

---

## `get_gpr_template_binding`

Fetches a GPR template binding by name.

```python
from egs.gpr_template_binding import get_gpr_template_binding

response = get_gpr_template_binding("gpr-template-binding-name")
```

**Parameters**:
- `binding_name` (`str`): Name of the GPR binding.

**Returns**: `GetGprTemplateBindingResponse` object.

---

## `list_gpr_template_bindings`

Lists all GPR template bindings.

```python
from egs.gpr_template_binding import list_gpr_template_bindings

response = list_gpr_template_bindings()
```

**Returns**: `ListGprTemplateBindingsResponse` object containing all bindings.

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

**Parameters**:
- Same as `create_gpr_template_binding`.

**Returns**: `UpdateGprTemplateBindingResponse`

---

## `delete_gpr_template_binding`

Deletes a GPR template binding.

```python
from egs.gpr_template_binding import delete_gpr_template_binding

response = delete_gpr_template_binding("gpr-template-binding-name")
```

**Parameters**:
- `binding_name` (`str`): Name of the binding to delete.

**Returns**: `DeleteGprTemplateBindingResponse`

---

## 🔗 Reference from Main README

To reference this file from your main `README.md`, add:

```markdown
## GPR Template Bindings API 📦

For full usage instructions, visit the [GPR Template Bindings Documentation](docs/gpr_template_binding.md).
```
