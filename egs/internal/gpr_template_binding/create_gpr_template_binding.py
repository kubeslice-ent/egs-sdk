from typing import List
from typing import List, 
from egs.util.string_util import serialize

class GprTemplateBindingCluster:
    """
    Represents a cluster entry in a GPR template binding request.
    """

    def __init__(
        self,
        cluster_name: str,
        default_template_name: str,
        templates: List[str]
    ):
        self.clusterName = cluster_name
        self.defaultTemplateName = default_template_name
        self.templates = templates

    def __str__(self):
        return serialize(self)


class CreateGprTemplateBindingRequest:
    """
    Request model for creating a GPR template binding.

    Attributes:
        workspace_name (str): The workspace/slice name.
        clusters (List[GprTemplateBindingCluster]): Optional list of clusters.
        enable_auto_gpr (bool): Flag to enable auto GPR.
    """

    def __init__(
        self,
        workspace_name: str,
        clusters: List[GprTemplateBindingCluster],
        enable_auto_gpr: bool
    ):
        self.workspaceName = workspace_name
        self.clusters = clusters
        self.enableAutoGPR = enable_auto_gpr

    def __str__(self):
        return serialize(self)


class CreateGprTemplateBindingResponse:
    """
    Response model for a successful GPR template binding creation.

    Attributes:
        name (str): Name of the binding.
        namespace (str): Namespace where it's created.
        clusters (List[GprTemplateBindingCluster]): Cluster bindings.
        enable_auto_gpr (bool): Whether auto GPR is enabled.
    """

    def __init__(
        self,
        name: str,
        namespace: str,
        clusters: List[dict],
        enableAutoGPR: bool
    ):
        self.name = name
        self.namespace = namespace
        self.clusters = [
            GprTemplateBindingCluster(
                cluster_name=c.get("clusterName"),
                default_template_name=c.get("defaultTemplateName"),
                templates=c.get("templates", [])
            ) for c in clusters
        ]
        self.enable_auto_gpr = enableAutoGPR

    def __str__(self):
        return serialize(self)

