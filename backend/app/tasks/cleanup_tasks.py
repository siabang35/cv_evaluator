from app.tasks.celery_config import celery_app
from app.database import execute_query
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)


@celery_app.task
def cleanup_old_jobs():
    """
    Clean up evaluation jobs older than 30 days.
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        query = """
            DELETE FROM evaluation_jobs
            WHERE created_at < %s
            AND status IN ('completed', 'failed')
        """
        
        deleted_count = execute_query(query, (cutoff_date,), fetch=False)
        logger.info(f"Cleaned up {deleted_count} old evaluation jobs")
        
        return {"deleted_count": deleted_count, "cutoff_date": cutoff_date.isoformat()}
    
    except Exception as e:
        logger.error(f"Failed to cleanup old jobs: {str(e)}")
        raise


@celery_app.task
def cleanup_old_documents():
    """
    Clean up uploaded documents older than 30 days.
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Get documents to delete
        query = """
            SELECT id, file_path FROM documents
            WHERE uploaded_at < %s
        """
        
        documents = execute_query(query, (cutoff_date,))
        
        deleted_files = 0
        deleted_records = 0
        
        for doc in documents:
            # Delete physical file
            if os.path.exists(doc['file_path']):
                try:
                    os.remove(doc['file_path'])
                    deleted_files += 1
                except Exception as e:
                    logger.warning(f"Failed to delete file {doc['file_path']}: {str(e)}")
            
            # Delete database record
            delete_query = "DELETE FROM documents WHERE id = %s"
            execute_query(delete_query, (doc['id'],), fetch=False)
            deleted_records += 1
        
        logger.info(f"Cleaned up {deleted_files} files and {deleted_records} document records")
        
        return {
            "deleted_files": deleted_files,
            "deleted_records": deleted_records,
            "cutoff_date": cutoff_date.isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to cleanup old documents: {str(e)}")
        raise
