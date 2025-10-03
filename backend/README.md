# CV Evaluator Backend - FastAPI

AI-powered backend service for automated CV and project report evaluation using LLM chaining and RAG.

## Architecture Overview

This backend implements a sophisticated AI evaluation pipeline with:

- **FastAPI** for high-performance async API endpoints
- **Supabase (PostgreSQL)** for data persistence
- **ChromaDB** for vector embeddings and RAG
- **OpenAI GPT-4** for LLM evaluation with chaining
- **Celery + Redis** for async job processing
- **PDF parsing** with PyPDF2 and pdfplumber

## Project Structure

\`\`\`
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration and environment variables
│   ├── database.py             # Supabase database connection
│   ├── models/                 # Pydantic models
│   │   ├── document.py
│   │   ├── evaluation.py
│   │   └── response.py
│   ├── routers/                # API route handlers
│   │   ├── upload.py
│   │   ├── evaluate.py
│   │   └── result.py
│   ├── services/               # Business logic
│   │   ├── document_service.py
│   │   ├── pdf_parser.py
│   │   ├── rag_service.py
│   │   ├── llm_service.py
│   │   └── evaluation_service.py
│   ├── tasks/                  # Celery async tasks
│   │   └── evaluation_tasks.py
│   └── utils/                  # Utility functions
│       ├── error_handler.py
│       └── retry_logic.py
├── requirements.txt
├── Dockerfile
└── .env.example
\`\`\`

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL with pgvector extension (Supabase)
- Redis (for Celery)
- OpenAI API key

### Installation

1. Clone the repository and navigate to backend directory:
\`\`\`bash
cd backend
\`\`\`

2. Create virtual environment:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

3. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. Configure environment variables:
\`\`\`bash
cp .env.example .env
# Edit .env with your credentials
\`\`\`

5. Run database migrations:
\`\`\`bash
# Execute SQL scripts in scripts/ folder against your Supabase database
\`\`\`

6. Start Redis (for Celery):
\`\`\`bash
redis-server
\`\`\`

7. Start Celery worker:
\`\`\`bash
celery -A app.tasks.evaluation_tasks worker --loglevel=info
\`\`\`

8. Start FastAPI server:
\`\`\`bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
\`\`\`

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

\`\`\`env
# Database
DATABASE_URL=postgresql://user:password@host:port/database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Redis
REDIS_URL=redis://localhost:6379/0

# Storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB

# LLM Configuration
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.3
MAX_RETRIES=3
RETRY_DELAY=2
\`\`\`

## Design Decisions

### 1. Async Job Processing
- Used Celery with Redis for handling long-running LLM evaluations
- Prevents API timeout issues
- Allows horizontal scaling of workers

### 2. RAG Implementation
- ChromaDB for vector storage (lightweight, easy to deploy)
- OpenAI text-embedding-ada-002 for embeddings
- Chunk size: 500 tokens with 50 token overlap
- Top-k retrieval: 5 most relevant chunks per query

### 3. LLM Chaining Strategy
- **Step 1**: Parse CV → Extract structured data
- **Step 2**: Retrieve relevant job description + CV rubric → Evaluate CV
- **Step 3**: Parse Project Report → Extract structured data
- **Step 4**: Retrieve case study brief + project rubric → Evaluate project
- **Step 5**: Synthesize all outputs → Generate overall summary

### 4. Error Handling
- Exponential backoff for LLM API failures (max 3 retries)
- Graceful degradation: partial results if one step fails
- Comprehensive logging for debugging
- Temperature control (0.3) for consistent outputs

### 5. Prompt Engineering
- System prompts with clear role definition
- Few-shot examples for consistent JSON output
- Explicit scoring criteria injection from rubrics
- Chain-of-thought reasoning for complex evaluations

## Testing

\`\`\`bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
\`\`\`

## Deployment

### Docker

\`\`\`bash
docker build -t cv-evaluator-backend .
docker run -p 8000:8000 --env-file .env cv-evaluator-backend
\`\`\`

### Production Considerations

- Use Gunicorn with Uvicorn workers
- Set up proper logging (structured JSON logs)
- Implement rate limiting
- Add authentication/authorization
- Use managed Redis (e.g., Upstash)
- Monitor LLM costs and token usage
