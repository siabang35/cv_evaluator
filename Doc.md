# Complete Setup Guide - CV Evaluator System

This guide will walk you through setting up the complete CV Evaluator system from scratch.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18 or higher) - [Download](https://nodejs.org/)
- **Python** (v3.10 or higher) - [Download](https://www.python.org/)
- **PostgreSQL** (v14 or higher) - Or use Supabase
- **Redis** (v6 or higher) - [Download](https://redis.io/)
- **Git** - [Download](https://git-scm.com/)

## Step 1: Clone the Repository

\`\`\`bash
git clone <your-repository-url>
cd cv-evaluator
\`\`\`

## Step 2: Set Up Supabase Database

### Option A: Use Supabase Cloud (Recommended)

1. Go to [supabase.com](https://supabase.com) and create a free account
2. Create a new project
3. Wait for the database to be provisioned (2-3 minutes)
4. Go to **Project Settings** → **Database**
5. Copy the **Connection String** (URI format)
6. Go to **Project Settings** → **API**
7. Copy the **Project URL** and **anon public** key
8. Copy the **service_role** key (keep this secret!)

### Option B: Use Local PostgreSQL

1. Install PostgreSQL locally
2. Create a new database:
\`\`\`bash
createdb cv_evaluator
\`\`\`
3. Your connection string will be:
\`\`\`
postgresql://postgres:password@localhost:5432/cv_evaluator
\`\`\`

## Step 3: Set Up Redis

### Option A: Use Local Redis

\`\`\`bash
# macOS (using Homebrew)
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Windows (using WSL or download from redis.io)
\`\`\`

### Option B: Use Redis Cloud

1. Go to [redis.com](https://redis.com) and create a free account
2. Create a new database
3. Copy the connection URL

## Step 4: Get Groq API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up or log in (free tier available)
3. Go to **API Keys** section
4. Click **Create API Key**
5. Copy the key (starts with `gsk_...`)
6. Groq offers free tier with generous rate limits!

**Available Models:**
- `llama-3.3-70b-versatile` - Best for complex reasoning (recommended)
- `llama-3.1-70b-versatile` - Fast and accurate
- `mixtral-8x7b-32768` - Large context window
- `gemma2-9b-it` - Lightweight and fast

## Step 5: Configure Backend Environment

1. Navigate to the backend directory:
\`\`\`bash
cd backend
\`\`\`

2. Copy the example environment file:
\`\`\`bash
cp .env.example .env
\`\`\`

3. Open `.env` and fill in your actual values:

\`\`\`bash
# Database (from Step 2)
DATABASE_URL=postgresql://postgres.xxxxx:password@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx

# Groq API (from Step 4) - FREE TIER AVAILABLE!
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx
GROQ_MODEL=llama-3.3-70b-versatile

# Embeddings (runs locally, no API key needed)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Redis (from Step 3)
REDIS_URL=redis://localhost:6379/0

# Generate a secret key
SECRET_KEY=$(openssl rand -hex 32)
\`\`\`

4. Install Python dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Step 6: Initialize Database

1. Run the database setup script:
\`\`\`bash
chmod +x scripts/setup_database.sh
./scripts/setup_database.sh
\`\`\`

Or manually run the SQL scripts:
\`\`\`bash
# Connect to your database and run:
psql $DATABASE_URL -f ../scripts/001_create_tables.sql
psql $DATABASE_URL -f ../scripts/002_seed_reference_documents.sql
\`\`\`

## Step 7: Ingest Reference Documents

1. Prepare your reference documents in the `backend/reference_docs/` directory:
   - `job_description.pdf` - The job description document
   - `case_study_brief.pdf` - The case study brief document
   - `cv_scoring_rubric.pdf` - CV evaluation criteria
   - `project_scoring_rubric.pdf` - Project evaluation criteria

2. Run the ingestion script (this will download the embedding model on first run):
\`\`\`bash
python scripts/ingest_reference_documents.py
\`\`\`

**Note:** The first run will download the Sentence Transformers model (~80MB). This is a one-time download and runs locally without any API calls.

## Step 8: Configure Frontend Environment

1. Navigate to the frontend directory:
\`\`\`bash
cd ..  # Go back to root
\`\`\`

2. Copy the example environment file:
\`\`\`bash
cp .env.local.example .env.local
\`\`\`

3. Open `.env.local` and configure:
\`\`\`bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_MAX_FILE_SIZE=10485760
NEXT_PUBLIC_POLL_INTERVAL=3000
\`\`\`

4. Install Node.js dependencies:
\`\`\`bash
npm install
\`\`\`

## Step 9: Start the Services

You'll need **4 terminal windows** to run all services:

### Terminal 1: Start Redis (if not running as service)
\`\`\`bash
redis-server
\`\`\`

### Terminal 2: Start FastAPI Backend
\`\`\`bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
\`\`\`

### Terminal 3: Start Celery Worker
\`\`\`bash
cd backend
celery -A app.tasks.celery_config.celery_app worker --loglevel=info
\`\`\`

### Terminal 4: Start Celery Beat (for scheduled tasks)
\`\`\`bash
cd backend
celery -A app.tasks.celery_config.celery_app beat --loglevel=info
\`\`\`

### Terminal 5: Start Next.js Frontend
\`\`\`bash
npm run dev
\`\`\`

## Step 10: Verify Everything Works

1. Open your browser and go to: `http://localhost:3000`
2. You should see the CV Evaluator interface
3. Try uploading a test CV and project report
4. Check that the evaluation starts and completes

## Troubleshooting

### Database Connection Issues

\`\`\`bash
# Test database connection
python -c "from app.database import engine; print(engine.connect())"
\`\`\`

### Redis Connection Issues

\`\`\`bash
# Test Redis connection
redis-cli ping
# Should return: PONG
\`\`\`

### Groq API Issues

\`\`\`bash
# Test Groq API connection
python -c "from groq import Groq; client = Groq(); print(client.models.list())"
\`\`\`

**Common Issues:**
- Rate limit exceeded: Groq free tier has rate limits, wait a moment and retry
- Invalid API key: Ensure your key starts with `gsk_`
- Model not found: Use one of the supported models listed in Step 4

### Embedding Model Issues

\`\`\`bash
# The embedding model downloads automatically on first use
# If you encounter issues, manually download:
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
\`\`\`

## Key Advantages of This Setup

### Cost-Effective
- **Groq**: Free tier with generous limits, extremely fast inference
- **Sentence Transformers**: Free local embeddings, no API costs
- **Supabase**: Free tier includes PostgreSQL with pgvector

### Performance
- **Groq**: 10-100x faster than OpenAI for inference
- **Local Embeddings**: No network latency, instant embedding generation
- **ChromaDB**: Fast vector similarity search

### Privacy
- **Local Embeddings**: Your documents never leave your server for embedding
- **Self-hosted Option**: Can run entirely on your infrastructure

## Production Deployment

### Using Docker Compose

\`\`\`bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
\`\`\`

### Environment Variables for Production

Update these in your `.env` file:

\`\`\`bash
APP_ENV=production
DEBUG=false
CORS_ORIGINS=https://your-frontend-domain.com
API_HOST=0.0.0.0
\`\`\`

## Next Steps

1. **Add your reference documents** to `backend/reference_docs/`
2. **Customize the evaluation prompts** in `backend/app/services/llm_service.py`
3. **Adjust scoring weights** in your `.env` file
4. **Set up monitoring** with Sentry (optional)
5. **Configure email notifications** (optional)

## Support

If you encounter any issues:

1. Check the logs in `backend/logs/app.log`
2. Verify all environment variables are set correctly
3. Ensure all services (Redis, PostgreSQL) are running
4. Check the troubleshooting section above

## Security Notes

- Never commit `.env` files to version control
- Keep your `SUPABASE_SERVICE_KEY` and `GROQ_API_KEY` secret
- Use strong passwords for production databases
- Enable SSL/TLS for production deployments
- Regularly rotate API keys and secrets
