"""
Script to ingest reference documents into the vector database.

This script:
1. Reads reference documents from the database
2. Chunks the content
3. Generates embeddings
4. Stores in ChromaDB for RAG retrieval

Usage:
    python scripts/ingest_reference_documents.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.rag_service import RAGService
from app.database import execute_query
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ingest_all_reference_documents():
    """
    Ingest all reference documents from the database into ChromaDB.
    """
    logger.info("Starting reference document ingestion...")
    
    # Initialize RAG service
    rag_service = RAGService()
    
    # Clear existing collection (optional - comment out to keep existing data)
    logger.info("Clearing existing vector database...")
    rag_service.clear_collection()
    
    # Fetch all reference documents from database
    query = """
        SELECT id, document_type, title, content, metadata
        FROM reference_documents
        ORDER BY document_type, created_at
    """
    
    documents = execute_query(query)
    
    if not documents:
        logger.warning("No reference documents found in database")
        return
    
    logger.info(f"Found {len(documents)} reference documents to ingest")
    
    # Ingest each document
    total_chunks = 0
    for doc in documents:
        logger.info(f"Ingesting: {doc['document_type']} - {doc['title']}")
        
        try:
            num_chunks = rag_service.ingest_reference_document(
                document_id=str(doc['id']),
                document_type=doc['document_type'],
                title=doc['title'],
                content=doc['content'],
                metadata=doc['metadata'] if doc['metadata'] else {}
            )
            
            total_chunks += num_chunks
            logger.info(f"  ✓ Created {num_chunks} chunks")
            
        except Exception as e:
            logger.error(f"  ✗ Failed to ingest document: {str(e)}")
            continue
    
    # Get collection stats
    stats = rag_service.get_collection_stats()
    logger.info(f"\nIngestion complete!")
    logger.info(f"Total documents: {len(documents)}")
    logger.info(f"Total chunks: {total_chunks}")
    logger.info(f"Collection stats: {stats}")


if __name__ == "__main__":
    try:
        ingest_all_reference_documents()
    except Exception as e:
        logger.error(f"Ingestion failed: {str(e)}")
        sys.exit(1)
