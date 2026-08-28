from typing import List, Optional

from egs.util.string_util import serialize


# ----- Request bodies (serialized to JSON and sent to egs-core-apis) -----
# Attribute names here become the JSON keys on the wire (see
# EgsCoreApisClient.invoke_sdk_operation, which serializes via o.__dict__), so
# they intentionally use the exact keys the relay expects.


class CreateContinuumGroupRequest(object):
    def __init__(self, name: str, label: str, icon: str):
        self.name = name
        self.label = label
        self.icon = icon

    def __str__(self):
        return serialize(self)


class UpdateContinuumGroupBody(object):
    # The group name is supplied as a query parameter (?name=), so only the
    # mutable fields travel in the body.
    def __init__(self, label: str, icon: str):
        self.label = label
        self.icon = icon

    def __str__(self):
        return serialize(self)


# ----- Response objects (built from api_response.data, whose keys are the
# camelCase keys the relay returns) -----


class ContinuumGroup(object):
    def __init__(
        self,
        name: str = None,
        label: str = None,
        icon: str = None,
        clusters: Optional[List[str]] = None,
        createdTimestamp: str = None,
        *args,
        **kwargs
    ):
        self.name = name
        self.label = label
        self.icon = icon
        self.clusters = clusters if clusters is not None else []
        self.created_timestamp = createdTimestamp

    def __str__(self):
        return serialize(self)


class ListContinuumGroupsResponse(object):
    def __init__(self, continuumGroups: Optional[List[dict]] = None, *args, **kwargs):
        self.continuum_groups = (
            [ContinuumGroup(**g) for g in continuumGroups] if continuumGroups else []
        )

    def __str__(self):
        return serialize(self)


class DeleteContinuumGroupResponse(object):
    def __init__(self, message: str = None, status: str = None, *args, **kwargs):
        self.message = message
        self.status = status

    def __str__(self):
        return serialize(self)


class ContinuumMetrics(object):
    # The three blocks are passed through verbatim from the gateway (dicts /
    # lists), so they are exposed as-is for the caller to consume.
    def __init__(
        self,
        overallMetrics: dict = None,
        tierCards: Optional[List[dict]] = None,
        workspaceTierMatrix: Optional[List[dict]] = None,
        *args,
        **kwargs
    ):
        self.overall_metrics = overallMetrics
        self.tier_cards = tierCards if tierCards is not None else []
        self.workspace_tier_matrix = (
            workspaceTierMatrix if workspaceTierMatrix is not None else []
        )

    def __str__(self):
        return serialize(self)


class ContinuumGroupDetail(object):
    def __init__(
        self,
        tierSummary: dict = None,
        clusters: Optional[List[dict]] = None,
        activeWorkloads: Optional[List[dict]] = None,
        *args,
        **kwargs
    ):
        self.tier_summary = tierSummary
        self.clusters = clusters if clusters is not None else []
        self.active_workloads = activeWorkloads if activeWorkloads is not None else []

    def __str__(self):
        return serialize(self)


class CapacityLandscape(object):
    def __init__(self, capacityLandscape=None, *args, **kwargs):
        self.capacity_landscape = capacityLandscape

    def __str__(self):
        return serialize(self)
