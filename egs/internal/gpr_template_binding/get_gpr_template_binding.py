from typing import List, Dict
from egs.util.string_util import serialize


class GprTemplateBindingClusterStatus:
    """
    Represents the status of a cluster in the GPR template binding response.

    Attributes:
        cluster_name (str): Cluster name.
        default_template_name (str): Default template assigned to the cluster.
        templates (List[str]): List of templates used by this cluster.
        default_template_status (str): Status of the default template.
        template_status (Dict[str, str]): Status of each template (name → reason/status).
    """

    def __init__(
        self,
        cluster_name: str,
        default_template_name: str,
        templates: List[str],
        default_template_status: str,
        template_status: Dict[str, str]
    ):
        self.clusterName = cluster_name
        self.defaultTemplateName = default_template_name
        self.templates = templates
        self.defaultTemplateStatus = default_template_status
        self.templateStatus = template_status

    def __str__(self):
        return serialize(self)


class GetGprTemplateBindingResponse:
    """
    Response model for a GPR template binding fetch.

    Attributes:
        name (str): Name of the binding.
        clusters (List[GprTemplateBindingClusterStatus]): Cluster status list.
        enable_auto_gpr (bool): Whether auto GPR is enabled.
    """

    def __init__(
        self,
        name: str,
        clusters: List[dict],
        enableAutoGPR: bool
    ):
        self.name = name
        self.clusters = [
            GprTemplateBindingClusterStatus(
                cluster_name=c.get("clusterName"),
                default_template_name=c.get("defaultTemplateName"),
                templates=c.get("templates", []),
                default_template_status=c.get("defaultTemplateStatus", ""),
                template_status=c.get("templateStatus", {})
            )
            for c in clusters
        ]
        self.enable_auto_gpr = enableAutoGPR

    def __str__(self):
        return serialize(self)

