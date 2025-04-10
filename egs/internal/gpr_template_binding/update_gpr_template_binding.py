from typing import List, Dict
from egs.util.string_util import serialize


class GprTemplateBindingCluster:
    def __init__(self, clusterName: str, defaultTemplateName: str, templates: List[str]):
        self.clusterName = clusterName
        self.defaultTemplateName = defaultTemplateName
        self.templates = templates


class GprTemplateBindingClusterStatus:
    def __init__(
        self,
        clusterName: str,
        defaultTemplateName: str,
        templates: List[str],
        defaultTemplateStatus: str,
        templateStatus: Dict[str, str]
    ):
        self.clusterName = clusterName
        self.defaultTemplateName = defaultTemplateName
        self.templates = templates
        self.defaultTemplateStatus = defaultTemplateStatus
        self.templateStatus = templateStatus


class UpdateGprTemplateBindingRequest:
    def __init__(self, workspace_name: str, clusters: List[GprTemplateBindingCluster], enable_auto_gpr: bool):
        self.workspaceName = workspace_name
        self.clusters = [cluster.__dict__ for cluster in clusters]
        self.enableAutoGPR = enable_auto_gpr

    def __str__(self):
        return serialize(self)


class UpdateGprTemplateBindingResponse:
    def __init__(
        self,
        name: str,
        namespace: str,
        clusters: List[dict],
        enableAutoGPR: bool
    ):
        self.name = name
        self.namespace = namespace
        self.clusters = [GprTemplateBindingClusterStatus(**c) for c in clusters]
        self.enable_auto_gpr = enableAutoGPR

    def __str__(self):
        return serialize(self)
