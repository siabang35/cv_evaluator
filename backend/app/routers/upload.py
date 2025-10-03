from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
from app.models.document import UploadResponse, DocumentResponse
from app.services.document_service import DocumentService
from app.config import settings
import os
from uuid import uuid4


router = APIRouter()
document_service = DocumentService()


@router.post("/upload", response_model=UploadResponse)
async def upload_documents(
    cv: Optional[UploadFile] = File(None),
    project_report: Optional[UploadFile] = File(None)
):
    """
    Upload candidate CV and/or project report.
    
    Returns document IDs for later evaluation.
    """
    if not cv and not project_report:
        raise HTTPException(
            status_code=400,
            detail="At least one file (CV or Project Report) must be provided"
        )
    
    cv_doc = None
    project_doc = None
    
    try:
        # Upload CV
        if cv:
            # Validate file type
            if not cv.filename.endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail="CV must be a PDF file"
                )
            
            # Validate file size
            content = await cv.read()
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"CV file size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
                )
            
            # Save file
            file_id = str(uuid4())
            file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}_{cv.filename}")
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Store in database
            cv_doc = document_service.create_document(
                filename=cv.filename,
                file_type="cv",
                file_path=file_path,
                file_size=len(content),
                mime_type=cv.content_type or "application/pdf"
            )
        
        # Upload Project Report
        if project_report:
            # Validate file type
            if not project_report.filename.endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail="Project Report must be a PDF file"
                )
            
            # Validate file size
            content = await project_report.read()
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"Project Report file size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
                )
            
            # Save file
            file_id = str(uuid4())
            file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}_{project_report.filename}")
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Store in database
            project_doc = document_service.create_document(
                filename=project_report.filename,
                file_type="project_report",
                file_path=file_path,
                file_size=len(content),
                mime_type=project_report.content_type or "application/pdf"
            )
        
        return UploadResponse(
            cv_document=cv_doc,
            project_document=project_doc,
            message="Documents uploaded successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload documents: {str(e)}")
