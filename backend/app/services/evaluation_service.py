from app.database import execute_query, execute_query_one
from uuid import UUID
from typing import Optional, Dict


class EvaluationService:
    def document_exists(self, document_id: UUID) -> bool:
        """Check if a document exists"""
        query = "SELECT EXISTS(SELECT 1 FROM documents WHERE id = %s)"
        result = execute_query_one(query, (str(document_id),))
        return result['exists'] if result else False
    
    def create_evaluation_job(
        self,
        job_title: str,
        cv_document_id: UUID,
        project_document_id: UUID
    ) -> Dict:
        """Create a new evaluation job"""
        query = """
            INSERT INTO evaluation_jobs (job_title, cv_document_id, project_document_id, status)
            VALUES (%s, %s, %s, 'queued')
            RETURNING id, job_title, cv_document_id, project_document_id, status, created_at
        """
        result = execute_query_one(
            query,
            (job_title, str(cv_document_id), str(project_document_id))
        )
        return dict(result)
    
    def get_evaluation_job(self, job_id: UUID) -> Optional[Dict]:
        """Get an evaluation job by ID"""
        query = """
            SELECT id, job_title, cv_document_id, project_document_id, status,
                   cv_match_rate, cv_feedback, project_score, project_feedback,
                   overall_summary, error_message, created_at, completed_at
            FROM evaluation_jobs
            WHERE id = %s
        """
        result = execute_query_one(query, (str(job_id),))
        return dict(result) if result else None
    
    def update_job_status(self, job_id: UUID, status: str, error_message: Optional[str] = None):
        """Update evaluation job status"""
        if error_message:
            query = """
                UPDATE evaluation_jobs
                SET status = %s, error_message = %s, updated_at = NOW()
                WHERE id = %s
            """
            execute_query(query, (status, error_message, str(job_id)), fetch=False)
        else:
            query = """
                UPDATE evaluation_jobs
                SET status = %s, updated_at = NOW()
                WHERE id = %s
            """
            execute_query(query, (status, str(job_id)), fetch=False)
    
    def update_job_results(
        self,
        job_id: UUID,
        cv_match_rate: Optional[float] = None,
        cv_feedback: Optional[str] = None,
        project_score: Optional[float] = None,
        project_feedback: Optional[str] = None,
        overall_summary: Optional[str] = None
    ):
        """Update evaluation job with results"""
        query = """
            UPDATE evaluation_jobs
            SET cv_match_rate = %s,
                cv_feedback = %s,
                project_score = %s,
                project_feedback = %s,
                overall_summary = %s,
                status = 'completed',
                completed_at = NOW(),
                updated_at = NOW()
            WHERE id = %s
        """
        execute_query(
            query,
            (cv_match_rate, cv_feedback, project_score, project_feedback, overall_summary, str(job_id)),
            fetch=False
        )
    
    def log_evaluation_step(
        self,
        job_id: UUID,
        step_name: str,
        llm_provider: str,
        llm_model: str,
        prompt_tokens: int,
        completion_tokens: int,
        response_time_ms: int,
        status: str,
        error_message: Optional[str] = None
    ):
        """Log an evaluation step for debugging and monitoring"""
        query = """
            INSERT INTO evaluation_logs
            (evaluation_job_id, step_name, llm_provider, llm_model,
             prompt_tokens, completion_tokens, total_tokens, response_time_ms,
             status, error_message)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        total_tokens = prompt_tokens + completion_tokens
        execute_query(
            query,
            (str(job_id), step_name, llm_provider, llm_model, prompt_tokens,
             completion_tokens, total_tokens, response_time_ms, status, error_message),
            fetch=False
        )
