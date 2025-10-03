#!/bin/bash

# Script to set up the database with all necessary tables and seed data

set -e

echo "=== CV Evaluator Database Setup ==="
echo ""

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL environment variable is not set"
    echo "Please set it in your .env file or export it"
    exit 1
fi

echo "Database URL: $DATABASE_URL"
echo ""

# Function to execute SQL file
execute_sql() {
    local file=$1
    echo "Executing: $file"
    psql "$DATABASE_URL" -f "$file"
    if [ $? -eq 0 ]; then
        echo "✓ Success"
    else
        echo "✗ Failed"
        exit 1
    fi
    echo ""
}

# Execute SQL scripts in order
echo "Step 1: Creating tables..."
execute_sql "scripts/001_create_tables.sql"

echo "Step 2: Seeding reference documents..."
execute_sql "scripts/002_seed_reference_documents.sql"

echo "=== Database setup complete! ==="
echo ""
echo "Next steps:"
echo "1. Run: python scripts/ingest_reference_documents.py"
echo "2. Start the API server: uvicorn app.main:app --reload"
echo "3. Start Celery worker: celery -A app.tasks.celery_config worker --loglevel=info"
