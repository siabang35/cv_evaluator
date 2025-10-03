"""
Script to test RAG retrieval functionality.

Usage:
    python scripts/test_rag_retrieval.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.rag_service import RAGService
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_cv_evaluation_context():
    """Test retrieval of CV evaluation context"""
    logger.info("\n=== Testing CV Evaluation Context Retrieval ===")
    
    rag_service = RAGService()
    
    job_title = "Backend Engineer"
    context = rag_service.get_context_for_cv_evaluation(job_title)
    
    logger.info(f"\nJob Title: {job_title}")
    logger.info(f"Retrieved Context Length: {len(context)} characters")
    logger.info(f"\nContext Preview:\n{context[:500]}...")


def test_project_evaluation_context():
    """Test retrieval of project evaluation context"""
    logger.info("\n=== Testing Project Evaluation Context Retrieval ===")
    
    rag_service = RAGService()
    
    context = rag_service.get_context_for_project_evaluation()
    
    logger.info(f"Retrieved Context Length: {len(context)} characters")
    logger.info(f"\nContext Preview:\n{context[:500]}...")


def test_custom_query():
    """Test custom query retrieval"""
    logger.info("\n=== Testing Custom Query Retrieval ===")
    
    rag_service = RAGService()
    
    query = "What are the requirements for error handling and resilience?"
    chunks = rag_service.retrieve_relevant_context(
        query=query,
        document_types=['project_rubric', 'case_study_brief'],
        top_k=3
    )
    
    logger.info(f"\nQuery: {query}")
    logger.info(f"Retrieved {len(chunks)} chunks:\n")
    
    for i, chunk in enumerate(chunks, 1):
        logger.info(f"Chunk {i}:")
        logger.info(f"  Document Type: {chunk['metadata']['document_type']}")
        logger.info(f"  Title: {chunk['metadata']['title']}")
        logger.info(f"  Distance: {chunk['distance']:.4f}")
        logger.info(f"  Text Preview: {chunk['text'][:200]}...")
        logger.info("")


def test_collection_stats():
    """Test collection statistics"""
    logger.info("\n=== Collection Statistics ===")
    
    rag_service = RAGService()
    stats = rag_service.get_collection_stats()
    
    logger.info(f"Collection Name: {stats['collection_name']}")
    logger.info(f"Total Chunks: {stats['total_chunks']}")


if __name__ == "__main__":
    try:
        test_collection_stats()
        test_cv_evaluation_context()
        test_project_evaluation_context()
        test_custom_query()
        
        logger.info("\n✓ All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        sys.exit(1)
