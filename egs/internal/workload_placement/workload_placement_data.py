from typing import Any, Dict, List

from egs.util.string_util import serialize


class ManifestResource(object):
    def __init__(self, name: str, manifest: Dict[str, Any]):
        self.name = name
        self.manifest = manifest

    def __str__(self):
        return serialize(self)


class WorkloadPlacementStep(object):
    def __init__(self, name: str, step_type: str = "manifest"):
        self.name = name
        self.type = step_type

    def __str__(self):
        return serialize(self)


class CreateWorkloadPlacementRequest(object):
    def __init__(
            self,
            workspace_name: str,
            workload_name: str,
            cluster_names: List[str],
            steps: List[WorkloadPlacementStep],
            manifest_resources: List[ManifestResource]
    ):
        self.workspaceName = workspace_name
        self.name = workload_name
        self.clusterNames = cluster_names
        self.steps = steps
        self.manifestResources = manifest_resources

    def __str__(self):
        return serialize(self)


class WorkloadPlacementResponse(object):
    """Generic response wrapper for Workload Placement APIs.

    The Workload Placement backend intentionally returns flexible data, so the
    SDK preserves it rather than imposing a schema that could become stale.
    """

    def __init__(self, data: Any):
        self.data = data

    def __str__(self):
        return serialize(self)
