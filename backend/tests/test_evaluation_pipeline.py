import pytest
from unittest.mock import Mock, patch
from app.tasks.evaluation_tasks import run_evaluation_pipeline
from app.utils.error_handler import PDFParsingError, LLMError


def test_evaluation_pipeline_success():
    """Test successful evaluation pipeline execution"""
    with patch('app.tasks.evaluation_tasks.EvaluationService') as mock_eval_service, \
         patch('app.tasks.evaluation_tasks.DocumentService') as mock_doc_service, \
         patch('app.tasks.evaluation_tasks.PDFParser') as mock_parser, \
         patch('app.tasks.evaluation_tasks.RAGService') as mock_rag, \
         patch('app.tasks.evaluation_tasks.LLMService') as mock_llm:
        
        # Setup mocks
        mock_eval_service.return_value.get_evaluation_job.return_value = {
            'job_title': 'Backend Engineer',
            'cv_document_id': 'cv-123',
            'project_document_id': 'project-456'
        }
        
        mock_doc_service.return_value.get_document.return_value = {
            'file_path': '/path/to/file.pdf'
        }
        
        mock_parser.return_value.parse_cv.return_value = {
            'cleaned_text': 'CV content'
        }
        
        mock_llm.return_value.parse_cv_to_structured_data.return_value = {
            'parsed_data': {},
            'usage': {'prompt_tokens': 100, 'completion_tokens': 50, 'response_time_ms': 1000}
        }
        
        # Execute
        result = run_evaluation_pipeline('job-123')
        
        # Assert
        assert result['status'] == 'completed'
        assert result['job_id'] == 'job-123'


def test_evaluation_pipeline_pdf_parsing_error():
    """Test handling of PDF parsing errors"""
    with patch('app.tasks.evaluation_tasks.EvaluationService') as mock_eval_service, \
         patch('app.tasks.evaluation_tasks.DocumentService') as mock_doc_service, \
         patch('app.tasks.evaluation_tasks.PDFParser') as mock_parser:
        
        # Setup mocks
        mock_eval_service.return_value.get_evaluation_job.return_value = {
            'job_title': 'Backend Engineer',
            'cv_document_id': 'cv-123',
            'project_document_id': 'project-456'
        }
        
        mock_doc_service.return_value.get_document.return_value = {
            'file_path': '/path/to/file.pdf'
        }
        
        # Simulate PDF parsing error
        mock_parser.return_value.parse_cv.side_effect = Exception("Failed to parse PDF")
        
        # Execute
        result = run_evaluation_pipeline('job-123')
        
        # Assert
        assert result['status'] == 'failed'
        assert 'error' in result
