from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class DocumentUpload(BaseModel):
    filename: str
    file_type: str  # 'cv' or 'project_report'
    file_size: int
    mime_type: str


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    file_type: str
    file_path: str
    file_size: int
    mime_type: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    cv_document: Optional[DocumentResponse] = None
    project_document: Optional[DocumentResponse] = None
    message: str
