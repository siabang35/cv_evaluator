import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from app.config import settings
from app.database import execute_query, execute_query_one
import tiktoken
import uuid


class RAGService:
    def __init__(self):
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Using all-MiniLM-L6-v2: fast, efficient, and works well for semantic search
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="reference_documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize tokenizer for chunking
        self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        
        # Chunking parameters
        self.chunk_size = 500  # tokens
        self.chunk_overlap = 50  # tokens
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks based on token count.
        """
        tokens = self.tokenizer.encode(text)
        chunks = []
        
        start = 0
        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
            start += self.chunk_size - self.chunk_overlap
        
        return chunks
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using Sentence Transformers.
        Replaced OpenAI embeddings with local Sentence Transformers model
        """
        embedding = self.embedding_model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    def ingest_reference_document(
        self,
        document_id: str,
        document_type: str,
        title: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """
        Ingest a reference document into the vector database.
        
        Steps:
        1. Chunk the document text
        2. Generate embeddings for each chunk
        3. Store in ChromaDB with metadata
        """
        # Chunk the document
        chunks = self.chunk_text(content)
        
        # Prepare data for ChromaDB
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for idx, chunk in enumerate(chunks):
            # Generate embedding
            embedding = self.generate_embedding(chunk)
            
            # Create unique ID
            chunk_id = f"{document_id}_chunk_{idx}"
            
            # Prepare metadata
            chunk_metadata = {
                "document_id": document_id,
                "document_type": document_type,
                "title": title,
                "chunk_index": idx,
                "total_chunks": len(chunks)
            }
            
            if metadata:
                chunk_metadata.update(metadata)
            
            ids.append(chunk_id)
            embeddings.append(embedding)
            documents.append(chunk)
            metadatas.append(chunk_metadata)
        
        # Add to ChromaDB collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        return len(chunks)
    
    def retrieve_relevant_context(
        self,
        query: str,
        document_types: List[str],
        top_k: int = 5
    ) -> List[Dict]:
        """
        Retrieve relevant context chunks for a query.
        
        Args:
            query: The search query
            document_types: Filter by document types (e.g., ['job_description', 'cv_rubric'])
            top_k: Number of top results to return
        
        Returns:
            List of relevant chunks with metadata
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k * 2,  # Get more results for filtering
            where={"document_type": {"$in": document_types}} if document_types else None
        )
        
        # Format results
        relevant_chunks = []
        if results['documents'] and results['documents'][0]:
            for idx, doc in enumerate(results['documents'][0][:top_k]):
                relevant_chunks.append({
                    "text": doc,
                    "metadata": results['metadatas'][0][idx],
                    "distance": results['distances'][0][idx] if results.get('distances') else None
                })
        
        return relevant_chunks
    
    def get_context_for_cv_evaluation(self, job_title: str) -> str:
        """
        Retrieve relevant context for CV evaluation.
        
        Retrieves:
        - Job description requirements
        - CV scoring rubric
        """
        query = f"Evaluate CV for {job_title} position. Technical skills, experience level, achievements, cultural fit."
        
        chunks = self.retrieve_relevant_context(
            query=query,
            document_types=['job_description', 'cv_rubric'],
            top_k=5
        )
        
        # Combine chunks into context
        context_parts = []
        for chunk in chunks:
            doc_type = chunk['metadata']['document_type']
            title = chunk['metadata']['title']
            text = chunk['text']
            context_parts.append(f"[{doc_type.upper()} - {title}]\n{text}\n")
        
        return "\n".join(context_parts)
    
    def get_context_for_project_evaluation(self) -> str:
        """
        Retrieve relevant context for project report evaluation.
        
        Retrieves:
        - Case study brief requirements
        - Project scoring rubric
        """
        query = "Evaluate project report. Correctness, code quality, resilience, error handling, documentation, creativity."
        
        chunks = self.retrieve_relevant_context(
            query=query,
            document_types=['case_study_brief', 'project_rubric'],
            top_k=5
        )
        
        # Combine chunks into context
        context_parts = []
        for chunk in chunks:
            doc_type = chunk['metadata']['document_type']
            title = chunk['metadata']['title']
            text = chunk['text']
            context_parts.append(f"[{doc_type.upper()} - {title}]\n{text}\n")
        
        return "\n".join(context_parts)
    
    def clear_collection(self):
        """Clear all documents from the collection (useful for re-ingestion)"""
        self.chroma_client.delete_collection("reference_documents")
        self.collection = self.chroma_client.get_or_create_collection(
            name="reference_documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the vector database"""
        count = self.collection.count()
        return {
            "total_chunks": count,
            "collection_name": self.collection.name
        }
