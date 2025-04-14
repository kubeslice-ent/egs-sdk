# 🧠 GPR Template Binding SDK

This module provides SDK functions for managing **GPR Template Bindings** in EGS (Elastic GPU Service).  
GPR bindings connect GPU templates to specific clusters under a workspace (slice) and optionally enable automated GPU provisioning.

---

## ⚙️ Functions Overview

- [`create_gpr_template_binding`](#create_gpr_template_binding)
- [`get_gpr_template_binding`](#get_gpr_template_binding)
- [`list_gpr_template_bindings`](#list_gpr_template_bindings)
- [`update_gpr_template_binding`](#update_gpr_template_binding)
- [`delete_gpr_template_binding`](#delete_gpr_template_binding)

---

## 🔧 `create_gpr_template_binding`

Creates a new GPR Template Binding to associate clusters with GPU resource templates.

### ✅ Function Signature
```python
create_gpr_template_binding(
    workspace_name: str,
    clusters: List[Dict],
    enable_auto_gpr: bool,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> CreateGprTemplateBindingResponse

📥 Parameters
Name	Type	Description
workspace_name	str	The workspace (slice) name.
clusters	List[Dict]	List of cluster template configurations.
enable_auto_gpr	bool	Enable automatic GPR provisioning.
authenticated_session	Optional	Auth session (optional).
🧾 Cluster Dict Format

{
    "clusterName": "worker-1",
    "defaultTemplateName": "template-1",
    "templates": ["template-1", "fallback-template"]
}

📤 Returns

CreateGprTemplateBindingResponse — includes name, namespace, clusters, and policy flags.
▶️ Example

create_gpr_template_binding(
    workspace_name="ai-team",
    clusters=[
        {
            "clusterName": "worker-1",
            "defaultTemplateName": "a100-high",
            "templates": ["a100-high", "a100-low"]
        }
    ],
    enable_auto_gpr=True
)

📥 get_gpr_template_binding

Fetches an existing GPR Template Binding by name.
✅ Function Signature

get_gpr_template_binding(
    binding_name: str,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> GetGprTemplateBindingResponse

📥 Parameters
Name	Type	Description
binding_name	str	Name of the GPR Template Binding
authenticated_session	Optional	Optional auth session
📤 Returns

GetGprTemplateBindingResponse with:

    name, enable_auto_gpr

    List of clusters, each with:

        clusterName, defaultTemplateName, templates

        defaultTemplateStatus, templateStatus (map of name → status)

▶️ Example

resp = get_gpr_template_binding("ai-team")
print(resp.name)

📋 list_gpr_template_bindings

Lists all GPR Template Bindings across the tenant.
✅ Function Signature

list_gpr_template_bindings(
    authenticated_session: Optional[AuthenticatedSession] = None
) -> ListGprTemplateBindingsResponse

📤 Returns

ListGprTemplateBindingsResponse with:

    templateBindings: List of GetGprTemplateBindingResponse

▶️ Example

resp = list_gpr_template_bindings()
for b in resp.templateBindings:
    print(b.name)

✏️ update_gpr_template_binding

Updates the cluster/template mapping or policy on an existing binding.
✅ Function Signature

update_gpr_template_binding(
    workspace_name: str,
    clusters: List[Dict],
    enable_auto_gpr: bool,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> UpdateGprTemplateBindingResponse

📥 Parameters

Same as create_gpr_template_binding.
📤 Returns

UpdateGprTemplateBindingResponse — empty structure on success.
▶️ Example

update_gpr_template_binding(
    workspace_name="ai-team",
    clusters=[
        {
            "clusterName": "worker-1",
            "defaultTemplateName": "new-template",
            "templates": ["new-template", "legacy-template"]
        }
    ],
    enable_auto_gpr=False
)

🗑️ delete_gpr_template_binding

Deletes a binding by name.
✅ Function Signature

delete_gpr_template_binding(
    binding_name: str,
    authenticated_session: Optional[AuthenticatedSession] = None
) -> DeleteGprTemplateBindingResponse

📥 Parameters
Name	Type	Description
binding_name	str	Name of the binding to delete
authenticated_session	Optional	Auth session
📤 Returns

DeleteGprTemplateBindingResponse — empty on success.
▶️ Example

delete_gpr_template_binding("ai-team")

✅ Authentication

All functions optionally accept a shared AuthenticatedSession. If not passed, it defaults to the active session:

import egs
session = egs.get_authenticated_session()

You can pass it explicitly:

create_gpr_template_binding(..., authenticated_session=session)