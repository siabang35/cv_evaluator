"""
Script to add a custom reference document to the database and vector store.

Usage:
    python scripts/add_custom_reference_document.py \
        --type job_description \
        --title "Senior Backend Engineer" \
        --file path/to/document.txt
"""

import sys
import os
import argparse
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.rag_service import RAGService
from app.database import execute_query_one
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def add_reference_document(doc_type: str, title: str, content: str, metadata: dict = None):
    """
    Add a reference document to the database and ingest into vector store.
    """
    logger.info(f"Adding reference document: {doc_type} - {title}")
    
    # Insert into database
    query = """
        INSERT INTO reference_documents (document_type, title, content, metadata)
        VALUES (%s, %s, %s, %s)
        RETURNING id, document_type, title
    """
    
    metadata_json = json.dumps(metadata) if metadata else None
    result = execute_query_one(query, (doc_type, title, content, metadata_json))
    
    if not result:
        raise Exception("Failed to insert document into database")
    
    doc_id = str(result['id'])
    logger.info(f"Document inserted with ID: {doc_id}")
    
    # Ingest into vector database
    rag_service = RAGService()
    num_chunks = rag_service.ingest_reference_document(
        document_id=doc_id,
        document_type=doc_type,
        title=title,
        content=content,
        metadata=metadata or {}
    )
    
    logger.info(f"Document ingested successfully with {num_chunks} chunks")
    return doc_id


def main():
    parser = argparse.ArgumentParser(description='Add a custom reference document')
    parser.add_argument('--type', required=True, 
                       choices=['job_description', 'case_study_brief', 'cv_rubric', 'project_rubric'],
                       help='Document type')
    parser.add_argument('--title', required=True, help='Document title')
    parser.add_argument('--file', required=True, help='Path to document file')
    parser.add_argument('--metadata', help='JSON metadata (optional)')
    
    args = parser.parse_args()
    
    # Read file content
    if not os.path.exists(args.file):
        logger.error(f"File not found: {args.file}")
        sys.exit(1)
    
    with open(args.file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse metadata if provided
    metadata = None
    if args.metadata:
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError:
            logger.error("Invalid JSON metadata")
            sys.exit(1)
    
    # Add document
    try:
        doc_id = add_reference_document(args.type, args.title, content, metadata)
        logger.info(f"Success! Document ID: {doc_id}")
    except Exception as e:
        logger.error(f"Failed to add document: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
