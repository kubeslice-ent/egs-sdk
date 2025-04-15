from typing import List
from egs.util.string_util import serialize
from .get_gpr_template import GetGprTemplateResponse  # Reusing the existing model


class ListGprTemplatesRequest:
    """Request model for listing GPR templates. No parameters are required."""

    def __str__(self):
        return serialize(self)


class ListGprTemplatesResponse:
    """Response model for listing GPR templates."""

    def __init__(self, items: List[dict]):
        self.items = [GetGprTemplateResponse(**item) for item in items]  # Convert dictionaries to objects

    def __str__(self):
        return serialize(self)
