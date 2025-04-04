from egs.util.string_util import serialize


class DeleteGprTemplateBindingRequest:
    """
    Request model for deleting a GPR template binding.

    Attributes:
        gpr_template_binding_name (str): Name of the binding to delete.
    """

    def __init__(self, gpr_template_binding_name: str):
        self.gprTemplateBindingName = gpr_template_binding_name

    def __str__(self):
        return serialize(self)


class DeleteGprTemplateBindingResponse:
    """
    Response model for a successful GPR template binding deletion.
    Currently an empty structure.
    """

    def __init__(self, *args, **kwargs):
        pass

    def __str__(self):
        return serialize(self)
