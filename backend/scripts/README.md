# Database and Ingestion Scripts

This directory contains scripts for setting up and managing the CV Evaluator system.

## Setup Scripts

### 1. Database Setup

Create all necessary tables and seed initial data:

\`\`\`bash
# Make script executable
chmod +x scripts/setup_database.sh

# Run setup
./scripts/setup_database.sh
\`\`\`

Or manually execute SQL files:

\`\`\`bash
psql $DATABASE_URL -f scripts/001_create_tables.sql
psql $DATABASE_URL -f scripts/002_seed_reference_documents.sql
\`\`\`

### 2. Ingest Reference Documents

Ingest reference documents into the vector database for RAG:

\`\`\`bash
python scripts/ingest_reference_documents.py
\`\`\`

This script:
- Reads all reference documents from the database
- Chunks the content (500 tokens with 50 token overlap)
- Generates embeddings using OpenAI
- Stores in ChromaDB for retrieval

### 3. Verify Setup

Check that all components are properly configured:

\`\`\`bash
python scripts/verify_setup.py
\`\`\`

This verifies:
- Database connection
- Reference documents exist
- Vector database is populated
- Redis is running
- OpenAI API key is valid

## Management Scripts

### Add Custom Reference Document

Add a new reference document to the system:

\`\`\`bash
python scripts/add_custom_reference_document.py \
    --type job_description \
    --title "Senior Backend Engineer" \
    --file path/to/document.txt \
    --metadata '{"department": "Engineering", "year": 2025}'
\`\`\`

Document types:
- `job_description` - Job requirements and responsibilities
- `case_study_brief` - Case study instructions
- `cv_rubric` - CV evaluation criteria
- `project_rubric` - Project evaluation criteria

### Test RAG Retrieval

Test the RAG retrieval system:

\`\`\`bash
python scripts/test_rag_retrieval.py
\`\`\`

This tests:
- CV evaluation context retrieval
- Project evaluation context retrieval
- Custom query retrieval
- Collection statistics

## Complete Setup Workflow

1. **Set up environment variables**:
   \`\`\`bash
   cp .env.example .env
   # Edit .env with your credentials
   \`\`\`

2. **Create database tables**:
   \`\`\`bash
   ./scripts/setup_database.sh
   \`\`\`

3. **Ingest reference documents**:
   \`\`\`bash
   python scripts/ingest_reference_documents.py
   \`\`\`

4. **Verify setup**:
   \`\`\`bash
   python scripts/verify_setup.py
   \`\`\`

5. **Start services**:
   \`\`\`bash
   # Terminal 1: API server
   uvicorn app.main:app --reload
   
   # Terminal 2: Celery worker
   celery -A app.tasks.celery_config worker --loglevel=info
   
   # Terminal 3: Frontend (in root directory)
   npm run dev
   \`\`\`

## Troubleshooting

### Vector database is empty

Run the ingestion script:
\`\`\`bash
python scripts/ingest_reference_documents.py
\`\`\`

### Database connection failed

Check your DATABASE_URL in .env:
\`\`\`bash
echo $DATABASE_URL
\`\`\`

### Redis connection failed

Start Redis:
\`\`\`bash
redis-server
\`\`\`

### OpenAI API failed

Verify your API key:
\`\`\`bash
echo $OPENAI_API_KEY
\`\`\`
