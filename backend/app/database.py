from supabase import create_client, Client
from app.config import settings
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager


# Supabase client for storage and auth
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Service role client for admin operations
supabase_admin: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = psycopg2.connect(settings.DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def execute_query(query: str, params: tuple = None, fetch: bool = True):
    """Execute a database query with parameters"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            return cursor.rowcount


def execute_query_one(query: str, params: tuple = None):
    """Execute a query and return one result"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()
