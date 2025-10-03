CREATE EXTENSION IF NOT EXISTS vector;


-- Create documents table to store uploaded CVs and Project Reports
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL, -- 'cv' or 'project_report'
    file_path TEXT NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create evaluation_jobs table to track async evaluation processes
CREATE TABLE IF NOT EXISTS evaluation_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_title VARCHAR(255) NOT NULL,
    cv_document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    project_document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'queued', -- 'queued', 'processing', 'completed', 'failed'
    cv_match_rate DECIMAL(3, 2), -- 0.00 to 1.00
    cv_feedback TEXT,
    project_score DECIMAL(3, 2), -- 1.00 to 5.00
    project_feedback TEXT,
    overall_summary TEXT,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create reference_documents table for system documents (Job Descriptions, Case Study Brief, Rubrics)
CREATE TABLE IF NOT EXISTS reference_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_type VARCHAR(100) NOT NULL, -- 'job_description', 'case_study_brief', 'cv_rubric', 'project_rubric'
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    file_path TEXT,
    metadata JSONB, -- Store additional metadata like job_title, department, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create vector_embeddings table for RAG system
CREATE TABLE IF NOT EXISTS vector_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reference_document_id UUID NOT NULL REFERENCES reference_documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding vector(1536), 
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create evaluation_logs table for tracking LLM calls and debugging
CREATE TABLE IF NOT EXISTS evaluation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evaluation_job_id UUID NOT NULL REFERENCES evaluation_jobs(id) ON DELETE CASCADE,
    step_name VARCHAR(100) NOT NULL, -- 'cv_parsing', 'cv_evaluation', 'project_parsing', 'project_evaluation', 'final_analysis'
    llm_provider VARCHAR(50),
    llm_model VARCHAR(100),
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    response_time_ms INTEGER,
    status VARCHAR(50), -- 'success', 'failed', 'retrying'
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_documents_file_type ON documents(file_type);
CREATE INDEX IF NOT EXISTS idx_evaluation_jobs_status ON evaluation_jobs(status);
CREATE INDEX IF NOT EXISTS idx_evaluation_jobs_created_at ON evaluation_jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reference_documents_type ON reference_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_vector_embeddings_reference_doc ON vector_embeddings(reference_document_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_logs_job_id ON evaluation_logs(evaluation_job_id);

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_evaluation_jobs_updated_at BEFORE UPDATE ON evaluation_jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reference_documents_updated_at BEFORE UPDATE ON reference_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
