from app.tasks.celery_config import celery_app
from app.services.evaluation_service import EvaluationService
from app.services.document_service import DocumentService
from app.services.pdf_parser import PDFParser
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService
from app.utils.error_handler import (
    handle_evaluation_error,
    format_error_message,
    PDFParsingError,
    LLMError,
    RAGError
)
from uuid import UUID
import logging
from celery.exceptions import SoftTimeLimitExceeded

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, soft_time_limit=1500)
def run_evaluation_pipeline(self, job_id: str):
    """
    Main evaluation pipeline task with comprehensive error handling.
    
    Steps:
    1. Parse CV → Extract structured data
    2. Retrieve job description + CV rubric → Evaluate CV
    3. Parse Project Report → Extract structured data
    4. Retrieve case study + project rubric → Evaluate project
    5. Synthesize → Generate overall summary
    """
    evaluation_service = EvaluationService()
    document_service = DocumentService()
    pdf_parser = PDFParser()
    rag_service = RAGService()
    llm_service = LLMService()
    
    job_uuid = UUID(job_id)
    
    try:
        # Update status to processing
        evaluation_service.update_job_status(job_uuid, 'processing')
        logger.info(f"[Job {job_id}] Starting evaluation pipeline")
        
        # Get job details
        job = evaluation_service.get_evaluation_job(job_uuid)
        if not job:
            raise Exception(f"Job {job_id} not found")
        
        job_title = job['job_title']
        cv_doc_id = job['cv_document_id']
        project_doc_id = job['project_document_id']
        
        # Get document paths
        cv_doc = document_service.get_document(cv_doc_id)
        project_doc = document_service.get_document(project_doc_id)
        
        if not cv_doc or not project_doc:
            raise Exception("Documents not found")
        
        # STEP 1: Parse CV
        logger.info(f"[Job {job_id}] Step 1: Parsing CV")
        try:
            cv_parsed = pdf_parser.parse_cv(cv_doc['file_path'])
            cv_structured = llm_service.parse_cv_to_structured_data(cv_parsed['cleaned_text'])
            
            evaluation_service.log_evaluation_step(
                job_uuid, 'cv_parsing', 'openai', 'gpt-4-turbo-preview',
                cv_structured['usage']['prompt_tokens'],
                cv_structured['usage']['completion_tokens'],
                cv_structured['usage']['response_time_ms'],
                'success'
            )
        except Exception as e:
            raise PDFParsingError(
                message=f"Failed to parse CV: {str(e)}",
                step="cv_parsing",
                details={"file_path": cv_doc['file_path']}
            )
        
        # STEP 2: Evaluate CV with RAG context
        logger.info(f"[Job {job_id}] Step 2: Evaluating CV")
        try:
            cv_rag_context = rag_service.get_context_for_cv_evaluation(job_title)
            cv_evaluation = llm_service.evaluate_cv(
                cv_structured['parsed_data'],
                job_title,
                cv_rag_context
            )
            
            evaluation_service.log_evaluation_step(
                job_uuid, 'cv_evaluation', 'openai', 'gpt-4-turbo-preview',
                cv_evaluation['usage']['prompt_tokens'],
                cv_evaluation['usage']['completion_tokens'],
                cv_evaluation['usage']['response_time_ms'],
                'success'
            )
        except Exception as e:
            raise LLMError(
                message=f"Failed to evaluate CV: {str(e)}",
                step="cv_evaluation",
                details={"job_title": job_title}
            )
        
        # STEP 3: Parse Project Report
        logger.info(f"[Job {job_id}] Step 3: Parsing project report")
        try:
            project_parsed = pdf_parser.parse_project_report(project_doc['file_path'])
            project_structured = llm_service.parse_project_report(project_parsed['cleaned_text'])
            
            evaluation_service.log_evaluation_step(
                job_uuid, 'project_parsing', 'openai', 'gpt-4-turbo-preview',
                project_structured['usage']['prompt_tokens'],
                project_structured['usage']['completion_tokens'],
                project_structured['usage']['response_time_ms'],
                'success'
            )
        except Exception as e:
            raise PDFParsingError(
                message=f"Failed to parse project report: {str(e)}",
                step="project_parsing",
                details={"file_path": project_doc['file_path']}
            )
        
        # STEP 4: Evaluate Project Report with RAG context
        logger.info(f"[Job {job_id}] Step 4: Evaluating project report")
        try:
            project_rag_context = rag_service.get_context_for_project_evaluation()
            project_evaluation = llm_service.evaluate_project_report(
                project_structured['parsed_data'],
                project_rag_context
            )
            
            evaluation_service.log_evaluation_step(
                job_uuid, 'project_evaluation', 'openai', 'gpt-4-turbo-preview',
                project_evaluation['usage']['prompt_tokens'],
                project_evaluation['usage']['completion_tokens'],
                project_evaluation['usage']['response_time_ms'],
                'success'
            )
        except Exception as e:
            raise LLMError(
                message=f"Failed to evaluate project: {str(e)}",
                step="project_evaluation"
            )
        
        # STEP 5: Generate Overall Summary
        logger.info(f"[Job {job_id}] Step 5: Generating overall summary")
        try:
            overall = llm_service.generate_overall_summary(
                cv_evaluation,
                project_evaluation,
                job_title
            )
            
            evaluation_service.log_evaluation_step(
                job_uuid, 'final_analysis', 'openai', 'gpt-4-turbo-preview',
                overall['usage']['prompt_tokens'],
                overall['usage']['completion_tokens'],
                overall['usage']['response_time_ms'],
                'success'
            )
        except Exception as e:
            raise LLMError(
                message=f"Failed to generate summary: {str(e)}",
                step="final_analysis"
            )
        
        # Update job with results
        evaluation_service.update_job_results(
            job_uuid,
            cv_match_rate=cv_evaluation['cv_match_rate'],
            cv_feedback=cv_evaluation['cv_feedback'],
            project_score=project_evaluation['project_score'],
            project_feedback=project_evaluation['project_feedback'],
            overall_summary=overall['overall_summary']
        )
        
        logger.info(f"[Job {job_id}] Evaluation pipeline completed successfully")
        return {"status": "completed", "job_id": job_id}
    
    except SoftTimeLimitExceeded:
        logger.error(f"[Job {job_id}] Task exceeded time limit")
        error_message = "Evaluation took too long and was terminated"
        evaluation_service.update_job_status(job_uuid, 'failed', error_message)
        return {"status": "failed", "job_id": job_id, "error": error_message}
    
    except (PDFParsingError, LLMError, RAGError) as e:
        logger.error(f"[Job {job_id}] Evaluation error: {str(e)}")
        error_info = handle_evaluation_error(e, e.step)
        error_message = format_error_message(error_info)
        
        # Log failed step
        evaluation_service.log_evaluation_step(
            job_uuid, e.step, 'openai', 'gpt-4-turbo-preview',
            0, 0, 0, 'failed', str(e)
        )
        
        # Update job status
        evaluation_service.update_job_status(job_uuid, 'failed', error_message)
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            retry_delay = 2 ** self.request.retries * 60  # 1min, 2min, 4min
            logger.info(f"[Job {job_id}] Retrying in {retry_delay}s (attempt {self.request.retries + 1})")
            raise self.retry(exc=e, countdown=retry_delay)
        
        return {"status": "failed", "job_id": job_id, "error": error_message}
    
    except Exception as e:
        logger.error(f"[Job {job_id}] Unexpected error: {str(e)}")
        error_info = handle_evaluation_error(e, "evaluation_pipeline")
        error_message = format_error_message(error_info)
        
        evaluation_service.update_job_status(job_uuid, 'failed', error_message)
        
        # Retry for unexpected errors
        if self.request.retries < self.max_retries:
            retry_delay = 2 ** self.request.retries * 60
            logger.info(f"[Job {job_id}] Retrying in {retry_delay}s (attempt {self.request.retries + 1})")
            raise self.retry(exc=e, countdown=retry_delay)
        
        return {"status": "failed", "job_id": job_id, "error": error_message}
