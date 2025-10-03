from app.database import execute_query, execute_query_one
from uuid import UUID
from typing import Optional, Dict


class DocumentService:
    def create_document(
        self,
        filename: str,
        file_type: str,
        file_path: str,
        file_size: int,
        mime_type: str
    ) -> Dict:
        """Create a new document record in the database"""
        query = """
            INSERT INTO documents (filename, file_type, file_path, file_size, mime_type)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, filename, file_type, file_path, file_size, mime_type, uploaded_at
        """
        result = execute_query_one(
            query,
            (filename, file_type, file_path, file_size, mime_type)
        )
        return dict(result)
    
    def get_document(self, document_id: UUID) -> Optional[Dict]:
        """Get a document by ID"""
        query = """
            SELECT id, filename, file_type, file_path, file_size, mime_type, uploaded_at
            FROM documents
            WHERE id = %s
        """
        result = execute_query_one(query, (str(document_id),))
        return dict(result) if result else None
    
    def document_exists(self, document_id: UUID) -> bool:
        """Check if a document exists"""
        query = "SELECT EXISTS(SELECT 1 FROM documents WHERE id = %s)"
        result = execute_query_one(query, (str(document_id),))
        return result['exists'] if result else False
