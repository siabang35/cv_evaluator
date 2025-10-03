from pydantic import BaseModel
from typing import Optional, Any


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class SuccessResponse(BaseModel):
    message: str
    data: Optional[Any] = None
