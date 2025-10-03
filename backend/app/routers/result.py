from fastapi import APIRouter, HTTPException, Path
from app.models.evaluation import EvaluationResultResponse, EvaluationResult
from app.services.evaluation_service import EvaluationService
from uuid import UUID


router = APIRouter()
evaluation_service = EvaluationService()


@router.get("/result/{job_id}", response_model=EvaluationResultResponse)
async def get_evaluation_result(
    job_id: UUID = Path(..., description="Evaluation job ID")
):
    """
    Retrieve the status and result of an evaluation job.
    
    Returns:
    - While queued or processing: status only
    - Once completed: status and full evaluation results
    - If failed: status and error message
    """
    try:
        job = evaluation_service.get_evaluation_job(job_id)
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Evaluation job with ID {job_id} not found"
            )
        
        # Build response based on status
        response = EvaluationResultResponse(
            id=job['id'],
            status=job['status'],
            created_at=job['created_at'],
            completed_at=job.get('completed_at')
        )
        
        # Add results if completed
        if job['status'] == 'completed':
            response.result = EvaluationResult(
                cv_match_rate=float(job['cv_match_rate']) if job.get('cv_match_rate') else None,
                cv_feedback=job.get('cv_feedback'),
                project_score=float(job['project_score']) if job.get('project_score') else None,
                project_feedback=job.get('project_feedback'),
                overall_summary=job.get('overall_summary')
            )
        
        # Add error message if failed
        if job['status'] == 'failed':
            response.error_message = job.get('error_message')
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve evaluation result: {str(e)}"
        )
