# Continuum Map (`egs.continuum`)

The continuum map models where GPU workloads land across the edge-to-core
"continuum": a set of named **continuum groups** (tiers), each a bucket of
clusters, ordered along a low-latency to high-compute axis. This module exposes
the same data the admin dashboard's Continuum Map renders, plus full CRUD over
the continuum groups themselves.

All calls go through `egs-core-apis`, which relays them to the KubeSlice API
gateway. Authenticate first with `egs.authenticate(...)`; every function accepts
an optional `authenticated_session` and otherwise uses the global session.

## Continuum group management

### `list_continuum_groups()` -> `ListContinuumGroupsResponse`

List all continuum groups. The order returned is the platform's configured tier
order (edge -> core).

```python
import egs
egs.authenticate("https://<endpoint>", api_key="<api-key>")

resp = egs.list_continuum_groups()
for group in resp.continuum_groups:
    print(group.name, group.label, group.clusters)
```

`ContinuumGroup` fields: `name`, `label`, `icon`, `clusters` (list of cluster
names), `created_timestamp`.

### `create_continuum_group(name, label, icon)` -> `ContinuumGroup`

```python
group = egs.create_continuum_group(
    name="Telco Far Edge",
    label="on premise far edge",
    icon="router",
)
```

### `update_continuum_group(name, label, icon)` -> `ContinuumGroup`

Updates the mutable fields (`label`, `icon`) of the group identified by `name`.

```python
egs.update_continuum_group("Telco Far Edge", label="far edge", icon="cloud")
```

### `delete_continuum_group(name)` -> `DeleteContinuumGroupResponse`

```python
result = egs.delete_continuum_group("Telco Far Edge")
print(result.status, result.message)
```

## Continuum map / dashboard views

### `get_continuum_metrics()` -> `ContinuumMetrics`

The aggregate continuum map: platform-wide totals, one card per tier, and the
workspace x tier placement matrix. Fields:

- `overall_metrics` (dict): totals such as `totalGPUs`, `allocatedGPUs`,
  `totalMemoryGB`, `allocatedMemoryGB`, `capacityUtilization`, `allocatedCost`.
- `tier_cards` (list): per-tier cards (`name`, `label`, `icon`, `clusters`,
  `totalGPUs`, `allocatedGPUs`, `totalMemoryGB`, `allocatedMemoryGB`,
  `allocatedCost`, `availableCost`).
- `workspace_tier_matrix` (list): per workspace, its `tierAllocations` with the
  workloads placed in each tier and the inter-tier `latency` maps.

```python
metrics = egs.get_continuum_metrics()
print(metrics.overall_metrics["capacityUtilization"])
for card in metrics.tier_cards:
    print(card["name"], card["allocatedGPUs"], "/", card["totalGPUs"])
```

These blocks are passed through verbatim from the gateway, so they are exposed
as plain dicts/lists rather than typed objects.

### `get_continuum_group_detail(name)` -> `ContinuumGroupDetail`

Detail view for one tier: `tier_summary` (dict), `clusters` (list), and
`active_workloads` (list).

```python
detail = egs.get_continuum_group_detail("Cust. Edge")
print(detail.tier_summary)
for wl in detail.active_workloads:
    print(wl["name"], wl["status"], wl["clusterName"])
```

### `get_capacity_landscape(workspace)` -> `CapacityLandscape`

Capacity landscape for a given workspace. The payload shape is passed through
verbatim and exposed as `capacity_landscape`.

```python
landscape = egs.get_capacity_landscape("mig-gpr")
print(landscape.capacity_landscape)
```

## Errors

Any non-200 response raises `egs.exceptions.UnhandledException`, carrying the
underlying `ApiResponse`. A missing/expired API key surfaces as `Unauthorized`
from the authentication layer, consistent with the rest of the SDK.

## Endpoint reference

| Function | SDK -> core-apis | core-apis -> gateway |
| --- | --- | --- |
| `list_continuum_groups` | `GET /api/v1/continuum-group/list` | `GET /api/v1/continuum-group/list` |
| `create_continuum_group` | `POST /api/v1/continuum-group/create` | `POST /api/v1/continuum-group/create` |
| `update_continuum_group` | `PUT /api/v1/continuum-group?name=` | `PUT /api/v1/continuum-group/{name}` |
| `delete_continuum_group` | `DELETE /api/v1/continuum-group?name=` | `DELETE /api/v1/continuum-group/{name}` |
| `get_continuum_metrics` | `GET /api/v1/continuum-group/metrics` | `GET /api/v1/dashboard/continuum-group-metrics/` |
| `get_continuum_group_detail` | `GET /api/v1/continuum-group/detail?name=` | `GET /api/v1/dashboard/continuum-group-detail/{name}` |
| `get_capacity_landscape` | `GET /api/v1/continuum-group/capacity-landscape?workspace=` | `GET /api/v1/dashboard/capacity-landscape/{workspace}` |
