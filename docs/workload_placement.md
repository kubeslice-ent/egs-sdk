# Kubernetes Manifest Workload Placement

The SDK can deploy customer-provided Kubernetes resources through the existing EGS Workload Placement API. This path is intended for workloads that are not represented by the KServe inference endpoint model, including customer-owned Docker images wrapped in ordinary Kubernetes manifests.

## Create from a manifest

```python
import egs

auth = egs.authenticate(
    endpoint="https://egs.example.com",
    api_key="YOUR_API_KEY",
)

with open("custom-inference.yaml", "r") as manifest_file:
    manifest = manifest_file.read()

result = egs.create_workload_placement_from_manifest(
    workspace_name="my-workspace",
    workload_name="custom-inference",
    cluster_names=["gpu-cluster-1"],
    manifest=manifest,
    authenticated_session=auth,
)

print(result.data)
```

`manifest` can be a YAML/JSON string, a Python dictionary, or a list of dictionaries. Multi-document YAML separated by `---` is supported. Each document must contain `apiVersion`, `kind`, and `metadata.name`.

Example manifest:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: custom-inference
spec:
  replicas: 1
  selector:
    matchLabels:
      app: custom-inference
  template:
    metadata:
      labels:
        app: custom-inference
    spec:
      containers:
        - name: server
          image: mycompany/my-model-server:v1
          ports:
            - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: custom-inference
spec:
  selector:
    app: custom-inference
  ports:
    - port: 80
      targetPort: 8000
```

## Inspect and delete

```python
placement = egs.get_workload_placement(
    "custom-inference",
    authenticated_session=auth,
)
print(placement.data)

workspace_placements = egs.list_workload_placements_by_workspace(
    "my-workspace",
    authenticated_session=auth,
)
print(workspace_placements.data)

egs.delete_workload_placement(
    "custom-inference",
    authenticated_session=auth,
)
```

The SDK performs only lightweight manifest validation. Kubernetes and the downstream Workload Placement service remain responsible for resource-specific validation and deployment behavior.
