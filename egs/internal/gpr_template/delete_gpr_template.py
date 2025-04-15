from egs.util.string_util import serialize


class DeleteGprTemplateRequest:
    def __init__(self, gpr_template_name: str):
        self.gprTemplateName = gpr_template_name

    def __str__(self):
        return serialize(self)


class DeleteGprTemplateResponse:
    def __init__(self, *args, **kwargs):
        pass  # No fields currently

    def __str__(self):
        return "{}"
