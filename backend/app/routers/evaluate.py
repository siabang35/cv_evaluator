from fastapi import APIRouter, HTTPException
from app.models.evaluation import EvaluationRequest, EvaluationJobResponse
from app.services.evaluation_service import EvaluationService
from app.tasks.evaluation_tasks import run_evaluation_pipeline

router = APIRouter()
evaluation_service = EvaluationService()


@router.post(
    "/evaluate",
    response_model=EvaluationJobResponse,
    summary="Start AI Evaluation",
    description="""
Trigger asynchronous **AI evaluation pipeline** for a candidate.

You need to provide:
- `job_title`: The role being evaluated (e.g. "Data Scientist").
- `cv_document_id`: Document ID of the uploaded CV.
- `project_document_id`: Document ID of the uploaded Project Report.

Returns a **job ID** and initial **status** so you can track progress.
    """
)
async def create_evaluation(request: EvaluationRequest):
    """
    Create a new evaluation job.
    """

    try:
        # Verify CV exists
        if not evaluation_service.document_exists(request.cv_document_id):
            raise HTTPException(
                status_code=404,
                detail=f"CV document with ID {request.cv_document_id} not found"
            )

        # Verify Project Report exists
        if not evaluation_service.document_exists(request.project_document_id):
            raise HTTPException(
                status_code=404,
                detail=f"Project document with ID {request.project_document_id} not found"
            )

        # Create evaluation job entry
        job = evaluation_service.create_evaluation_job(
            job_title=request.job_title,
            cv_document_id=request.cv_document_id,
            project_document_id=request.project_document_id,
        )

        # Kick off async pipeline
        run_evaluation_pipeline.delay(str(job["id"]))

        return EvaluationJobResponse(
            id=job["id"],
            status=job["status"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create evaluation job: {str(e)}"
        )
