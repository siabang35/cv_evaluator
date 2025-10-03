"""
Script to verify the complete system setup.

Checks:
1. Database connection
2. Reference documents in database
3. Vector database setup
4. Redis connection
5. Groq API key
6. Required directories

Usage:
    python scripts/verify_setup.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import execute_query_one
from app.services.rag_service import RAGService
from app.config import settings
import redis
from dotenv import load_dotenv
import logging
from groq import Groq

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_database():
    """Check database connection and tables"""
    logger.info("Checking database connection...")

    try:
        result = execute_query_one("SELECT COUNT(*) as count FROM reference_documents")
        count = result['count']
        logger.info(f"✓ Database connected. Found {count} reference documents")
        return True
    except Exception as e:
        logger.error(f"✗ Database connection failed: {str(e)}")
        return False


def check_vector_database():
    """Check vector database setup"""
    logger.info("Checking vector database...")

    try:
        rag_service = RAGService()
        stats = rag_service.get_collection_stats()
        logger.info(f"✓ Vector database connected. Total chunks: {stats['total_chunks']}")

        if stats['total_chunks'] == 0:
            logger.warning("⚠ Vector database is empty. Run: python scripts/ingest_reference_documents.py")

        return True
    except Exception as e:
        logger.error(f"✗ Vector database connection failed: {str(e)}")
        return False


def check_redis():
    """Check Redis connection"""
    logger.info("Checking Redis connection...")

    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        logger.info("✓ Redis connected")
        return True
    except Exception as e:
        logger.error(f"✗ Redis connection failed: {str(e)}")
        return False


def check_groq():
    """Check Groq API key"""
    logger.info("Checking Groq API...")

    try:
        client = Groq(api_key=settings.GROQ_API_KEY)
        models = client.models.list()
        if models and len(models.data) > 0:
            logger.info("✓ Groq API key valid")
            return True
        else:
            logger.warning("⚠ Groq API key valid but no models available")
            return True
    except Exception as e:
        logger.error(f"✗ Groq API check failed: {str(e)}")
        return False


def check_directories():
    """Check required directories"""
    logger.info("Checking directories...")

    directories = [
        settings.UPLOAD_DIR,
        settings.CHROMA_PERSIST_DIR
    ]

    all_exist = True
    for directory in directories:
        if os.path.exists(directory):
            logger.info(f"✓ Directory exists: {directory}")
        else:
            logger.warning(f"⚠ Directory missing: {directory} (will be created automatically)")
            all_exist = False

    return all_exist


def main():
    logger.info("=== CV Evaluator System Verification ===\n")

    checks = {
        "Database": check_database(),
        "Vector Database": check_vector_database(),
        "Redis": check_redis(),
        "Groq API": check_groq(),
        "Directories": check_directories()
    }

    logger.info("\n=== Verification Summary ===")

    all_passed = True
    for check_name, passed in checks.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{check_name}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        logger.info("\n✓ All checks passed! System is ready.")
        logger.info("\nTo start the system:")
        logger.info("1. Backend API: uvicorn app.main:app --reload")
        logger.info("2. Celery Worker: celery -A app.tasks.celery_config worker --loglevel=info")
        logger.info("3. Frontend: npm run dev")
        sys.exit(0)
    else:
        logger.error("\n✗ Some checks failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
