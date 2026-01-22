from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class ApiResponse(BaseModel):
    """Standard API response from EGS server."""

    status: str
    message: str
    status_code: int = Field(alias="statusCode")
    data: Optional[Union[Dict[str, Any], List[Any]]] = None
    error: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(populate_by_name=True)
