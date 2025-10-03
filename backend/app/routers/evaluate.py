from fastapi import APIRouter, HTTPException
from app.models.evaluation import EvaluationRequest, EvaluationJobResponse
from app.services.evaluation_service import EvaluationService
from app.tasks.evaluation_tasks import run_evaluation_pipeline


router = APIRouter()
evaluation_service = EvaluationService()


@router.post("/evaluate", response_model=EvaluationJobResponse)
async def create_evaluation(request: EvaluationRequest):
    """
    Trigger asynchronous AI evaluation pipeline.
    
    Returns a job ID to track the evaluation process.
    """
    try:
        # Verify documents exist
        cv_exists = evaluation_service.document_exists(request.cv_document_id)
        project_exists = evaluation_service.document_exists(request.project_document_id)
        
        if not cv_exists:
            raise HTTPException(
                status_code=404,
                detail=f"CV document with ID {request.cv_document_id} not found"
            )
        
        if not project_exists:
            raise HTTPException(
                status_code=404,
                detail=f"Project document with ID {request.project_document_id} not found"
            )
        
        # Create evaluation job
        job = evaluation_service.create_evaluation_job(
            job_title=request.job_title,
            cv_document_id=request.cv_document_id,
            project_document_id=request.project_document_id
        )
        
        # Trigger async evaluation task
        run_evaluation_pipeline.delay(str(job['id']))
        
        return EvaluationJobResponse(
            id=job['id'],
            status=job['status']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create evaluation job: {str(e)}"
        )
