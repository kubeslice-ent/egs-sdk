from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class ApiResponse(BaseModel):
    """Standard API response from EGS server."""

    status: str
    message: str
    status_code: int = Field(alias="statusCode")
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(populate_by_name=True)
