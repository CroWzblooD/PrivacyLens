"""
PrivacyLens Backend Main Application
Professional FastAPI backend for PII detection and redaction
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import os
import logging

from app.core.config import settings
from app.api.routes import router
from app.utils.helpers import setup_logging

# Setup logging
setup_logging("INFO")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 PrivacyLens Backend starting up...")
    logger.info(f"📍 Server will run on http://{settings.HOST}:{settings.PORT}")
    logger.info(f"📚 API Documentation: http://localhost:{settings.PORT}/docs")
    logger.info(f"🔗 Health Check: http://localhost:{settings.PORT}/api/health")
    logger.info("✅ All services initialized successfully")
    yield
    # Shutdown
    logger.info("🛑 PrivacyLens Backend shutting down...")
    logger.info("✅ Cleanup completed")

# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

# Include API routes
app.include_router(router, prefix="/api", tags=["PrivacyLens API"])

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API information"""
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{settings.API_TITLE}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .header {{ background: #007bff; color: white; padding: 20px; border-radius: 8px; }}
            .content {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 20px; }}
            .endpoint {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }}
            .status {{ color: #28a745; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{settings.API_TITLE}</h1>
                <p>{settings.API_DESCRIPTION}</p>
                <p>Version: {settings.API_VERSION}</p>
            </div>
            
            <div class="content">
                <h2>🟢 <span class="status">Backend is running successfully!</span></h2>
                
                <h3>📚 API Documentation</h3>
                <div class="endpoint">
                    <strong>Swagger UI:</strong> <a href="/docs" target="_blank">http://localhost:{settings.PORT}/docs</a>
                </div>
                <div class="endpoint">
                    <strong>ReDoc:</strong> <a href="/redoc" target="_blank">http://localhost:{settings.PORT}/redoc</a>
                </div>
                
                <h3>🔗 API Endpoints</h3>
                <div class="endpoint">
                    <strong>POST /api/upload</strong> - Upload PDF for processing
                </div>
                <div class="endpoint">
                    <strong>GET /api/status/{{job_id}}</strong> - Get processing status
                </div>
                <div class="endpoint">
                    <strong>GET /api/download/{{job_id}}</strong> - Download processed file
                </div>
                <div class="endpoint">
                    <strong>GET /api/health</strong> - Health check
                </div>
                
                <h3>🎯 Frontend Integration</h3>
                <p>This backend is designed to work with the React frontend. Make sure the frontend is configured to connect to <code>http://localhost:{settings.PORT}</code></p>
                
                <h3>🚀 Getting Started</h3>
                <ol>
                    <li>Upload a PDF file using POST /api/upload</li>
                    <li>Monitor processing status with GET /api/status/{{job_id}}</li>
                    <li>Download the redacted PDF with GET /api/download/{{job_id}}</li>
                </ol>
            </div>
        </div>
    </body>
    </html>
    """)

# Serve frontend static files if available
if os.path.exists("../frontend/dist"):
    app.mount("/static", StaticFiles(directory="../frontend/dist"), name="static")
    logger.info("Mounted frontend static files from ../frontend/dist")
elif os.path.exists("../frontend"):
    app.mount("/static", StaticFiles(directory="../frontend"), name="static")
    logger.info("Mounted frontend static files from ../frontend")



if __name__ == "__main__":
    print("🚀 Starting PrivacyLens Backend Server...")
    print(f"📱 API Server: http://localhost:{settings.PORT}")
    print(f"📚 API Documentation: http://localhost:{settings.PORT}/docs")
    print(f"🔗 Health Check: http://localhost:{settings.PORT}/api/health")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level="info"
    )