from typing import List
from .get_gpr_template_binding import GetGprTemplateBindingResponse
from egs.util.string_util import serialize


class ListGprTemplateBindingsRequest:
    """
    Request model for listing all GPR template bindings.
    """

    def __str__(self):
        return serialize(self)


class ListGprTemplateBindingsResponse:
    """
    Response model for listing GPR template bindings.

    Attributes:
        template_bindings (List[GetGprTemplateBindingResponse]): A list of
            GPR template binding responses.
    """

    def __init__(self, templateBindings: List[dict]):
        self.templateBindings: List[GetGprTemplateBindingResponse] = [
            GetGprTemplateBindingResponse(
                name=binding.get("name"),
                clusters=binding.get("clusters", []),
                enableAutoGPR=binding.get("enableAutoGPR", False)
            )
            for binding in templateBindings
        ]

    def __str__(self):
        return serialize(self)

