from typing import Optional, Dict, Any
import traceback
import logging

logger = logging.getLogger(__name__)


class EvaluationError(Exception):
    """Base exception for evaluation errors"""
    def __init__(self, message: str, step: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.step = step
        self.details = details or {}
        super().__init__(self.message)


class PDFParsingError(EvaluationError):
    """Exception for PDF parsing failures"""
    pass


class LLMError(EvaluationError):
    """Exception for LLM API failures"""
    pass


class RAGError(EvaluationError):
    """Exception for RAG retrieval failures"""
    pass


def handle_evaluation_error(error: Exception, step: str) -> Dict[str, str]:
    """
    Handle evaluation errors and return formatted error information.
    
    Args:
        error: The exception that occurred
        step: The evaluation step where error occurred
    
    Returns:
        Dictionary with error details
    """
    error_info = {
        "step": step,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc()
    }
    
    # Log the error
    logger.error(f"Evaluation error in step '{step}': {error_info}")
    
    return error_info


def format_error_message(error_info: Dict[str, str]) -> str:
    """
    Format error information into a user-friendly message.
    """
    return f"Evaluation failed at step '{error_info['step']}': {error_info['error_message']}"
