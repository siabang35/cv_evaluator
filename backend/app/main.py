from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import upload, evaluate, result
from app.middleware.error_middleware import setup_exception_handlers
from app.middleware.logging_middleware import log_requests_middleware
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="CV Evaluator API",
    description="""
    AI-powered CV and project report evaluation system using Groq API.
    
    ## Features
    
    * **Upload Documents** - Upload CV and project reports in PDF format
    * **AI Evaluation** - Get comprehensive evaluation using advanced AI models
    * **Results Management** - Retrieve and manage evaluation results
    * **RAG Support** - Retrieval-Augmented Generation for context-aware evaluation
    
    ## Authentication
    
    Currently, no authentication is required. This will be added in future versions.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Health",
            "description": "Health check endpoints"
        },
        {
            "name": "Upload",
            "description": "Document upload operations"
        },
        {
            "name": "Evaluation",
            "description": "CV and project evaluation operations"
        },
        {
            "name": "Results",
            "description": "Evaluation results retrieval"
        }
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.middleware("http")(log_requests_middleware)

# Setup exception handlers
setup_exception_handlers(app)

# Health check endpoint
@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description="Check if the API is running and healthy",
    response_description="Returns the health status of the API"
)
async def health_check():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        dict: Status and service name
    """
    return {
        "status": "healthy",
        "service": "cv-evaluator-api",
        "version": "1.0.0"
    }

# Include routers
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(evaluate.router, prefix="/api", tags=["Evaluation"])
app.include_router(result.router, prefix="/api", tags=["Results"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
