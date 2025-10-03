import os
import base64
from uuid import uuid4
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.document import UploadResponse
from app.services.document_service import DocumentService
from app.config import settings

router = APIRouter()
document_service = DocumentService()

# ---- Request Body ----
class UploadRequest(BaseModel):
    cv_base64: str | None = None
    project_base64: str | None = None

def safe_b64decode(data: str) -> bytes:
    """
    Decode Base64 string safely by:
    - stripping whitespace/newlines
    - adding padding if missing
    """
    data = data.strip().replace("\n", "").replace("\r", "")
    missing_padding = len(data) % 4
    if missing_padding:
        data += "=" * (4 - missing_padding)
    return base64.b64decode(data)

@router.post(
    "/upload",
    response_model=UploadResponse,
    summary="Upload CV & Project Report (JSON Base64)",
    description="""
Upload CV dan Project Report dalam bentuk **base64 string**.  
Minimal salah satu harus diisi.  
Keduanya akan disimpan di server, lalu ID dikembalikan untuk dipakai di `/evaluate`.
"""
)
async def upload_documents(request: UploadRequest):
    if not request.cv_base64 and not request.project_base64:
        raise HTTPException(
            status_code=400,
            detail="At least one file (CV or Project Report) must be provided"
        )

    cv_doc = None
    project_doc = None

    try:
        # Handle CV
        if request.cv_base64:
            content = safe_b64decode(request.cv_base64)
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"CV file size exceeds {settings.MAX_FILE_SIZE} bytes"
                )

            file_id = str(uuid4())
            filename = f"{file_id}_cv.pdf"
            file_path = os.path.join(settings.UPLOAD_DIR, filename)

            with open(file_path, "wb") as f:
                f.write(content)

            cv_doc = document_service.create_document(
                filename=filename,
                file_type="cv",
                file_path=file_path,
                file_size=len(content),
                mime_type="application/pdf"
            )

        # Handle Project Report
        if request.project_base64:
            content = safe_b64decode(request.project_base64)
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"Project Report file size exceeds {settings.MAX_FILE_SIZE} bytes"
                )

            file_id = str(uuid4())
            filename = f"{file_id}_project.pdf"
            file_path = os.path.join(settings.UPLOAD_DIR, filename)

            with open(file_path, "wb") as f:
                f.write(content)

            project_doc = document_service.create_document(
                filename=filename,
                file_type="project_report",
                file_path=file_path,
                file_size=len(content),
                mime_type="application/pdf"
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
