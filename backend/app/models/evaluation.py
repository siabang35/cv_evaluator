from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class EvaluationRequest(BaseModel):
    job_title: str = Field(..., min_length=1, max_length=255)
    cv_document_id: UUID
    project_document_id: UUID


class EvaluationJobResponse(BaseModel):
    id: UUID
    status: str  # 'queued', 'processing', 'completed', 'failed'
    
    class Config:
        from_attributes = True


class EvaluationResult(BaseModel):
    cv_match_rate: Optional[float] = None
    cv_feedback: Optional[str] = None
    project_score: Optional[float] = None
    project_feedback: Optional[str] = None
    overall_summary: Optional[str] = None


class EvaluationResultResponse(BaseModel):
    id: UUID
    status: str
    result: Optional[EvaluationResult] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
