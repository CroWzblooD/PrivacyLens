"""
API Routes for PrivacyLens Backend
"""

import os
import time
import logging
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.responses import FileResponse
from typing import Dict, Any

from ..core.config import settings
from ..services.pii_processor import PIIProcessorService
from ..utils.helpers import generate_unique_filename, is_pdf_file, get_file_size

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize PII processor service
pii_processor = PIIProcessorService()

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "message": "PrivacyLens backend is running",
        "version": "1.0.0"
    }

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    redaction_prompt: str = Form(default="hide all personal information")
) -> Dict[str, Any]:
    """
    Upload and process document
    
    Args:
        background_tasks: FastAPI background tasks
        file: Uploaded PDF file
        
    Returns:
        Job information dictionary
    """
    # Validate file type
    if not is_pdf_file(file.filename):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB")
    
    # Generate unique filename and paths
    unique_filename = generate_unique_filename(file.filename)
    input_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Save uploaded file
    try:
        with open(input_path, "wb") as buffer:
            buffer.write(content)
        logger.info(f"Saved uploaded file to {input_path}")
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")
    
    # Create processing job first to get the job ID
    try:
        job = pii_processor.create_processing_job(file.filename, input_path, "")
        logger.info(f"Created processing job {job.job_id}")
        
        # Now create output path using the actual job ID
        output_filename = f"{job.job_id}_redacted.pdf"
        output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
        
        # Update the job with the correct output path
        job.output_path = output_path
        
    except Exception as e:
        logger.error(f"Failed to create processing job: {e}")
        raise HTTPException(status_code=500, detail="Failed to create processing job")
    
    # Start background processing with redaction prompt
    logger.info(f"Redaction prompt: '{redaction_prompt}'")
    background_tasks.add_task(
        process_document_background, 
        job.job_id, 
        input_path, 
        output_path,
        redaction_prompt
    )
    
    return {
        "job_id": job.job_id,
        "filename": file.filename,
        "status": "processing",
        "message": "File uploaded successfully and processing started",
        "upload_timestamp": job.created_at
    }

async def process_document_background(job_id: str, input_path: str, output_path: str, redaction_prompt: str = "hide all personal information"):
    """
    Background task to process document with user-specified redaction preferences
    
    Args:
        job_id: Job identifier
        input_path: Input file path
        output_path: Output file path
        redaction_prompt: User's redaction preferences
    """
    try:
        logger.info(f"Starting background processing for job {job_id}")
        logger.info(f"Using redaction prompt: '{redaction_prompt}'")
        
        # Process the document with redaction prompt
        results = pii_processor.process_document(input_path, output_path, job_id, redaction_prompt)
        
        if not results["success"]:
            logger.error(f"Processing failed for job {job_id}: {results.get('error', 'Unknown error')}")
        else:
            logger.info(f"Processing completed successfully for job {job_id}")
            
    except Exception as e:
        logger.error(f"Background processing failed for job {job_id}: {e}")
        pii_processor.job_manager.mark_job_failed(job_id, str(e))

@router.get("/status/{job_id}")
async def get_processing_status(job_id: str) -> Dict[str, Any]:
    """
    Get processing status for a job
    
    Args:
        job_id: Job identifier
        
    Returns:
        Job status dictionary
    """
    status = pii_processor.get_job_status(job_id)
    
    if status:
        return status
    
    # Fallback: Check if output file exists (server may have restarted)
    output_path = os.path.join(settings.OUTPUT_DIR, f"{job_id}_redacted.pdf")
    if os.path.exists(output_path):
        return {
            "job_id": job_id,
            "filename": "unknown",
            "status": "completed",
            "progress": 100,
            "message": "Processing completed",
            "logs": ["✅ Document processing completed"],
            "results": {"total_detections": 0}
        }
    
    raise HTTPException(status_code=404, detail="Job not found")

@router.get("/download/{job_id}")
async def download_result(job_id: str) -> FileResponse:
    """
    Download processed document
    
    Args:
        job_id: Job identifier
        
    Returns:
        FileResponse with processed PDF
    """
    # Get job status
    job_status = pii_processor.get_job_status(job_id)
    
    if job_status:
        if job_status["status"] != "completed":
            raise HTTPException(status_code=400, detail="Processing not completed")
        
        # Try to find output file from job
        job = pii_processor.job_manager.get_job(job_id)
        if job and os.path.exists(job.output_path):
            output_path = job.output_path
            filename_prefix = f"redacted_{job.filename}"
        else:
            # Fallback: Look for file directly
            output_path = os.path.join(settings.OUTPUT_DIR, f"{job_id}_redacted.pdf")
            filename_prefix = "redacted_document.pdf"
    else:
        # Fallback: Look for file directly (in case server restarted)
        output_path = os.path.join(settings.OUTPUT_DIR, f"{job_id}_redacted.pdf")
        filename_prefix = "redacted_document.pdf"
    
    if not os.path.exists(output_path):
        # Try alternative filename patterns that might exist
        import glob
        pattern1 = os.path.join(settings.OUTPUT_DIR, f"{job_id}_*_redacted.pdf")
        pattern2 = os.path.join(settings.OUTPUT_DIR, f"{job_id}*redacted.pdf")
        
        possible_files = glob.glob(pattern1) + glob.glob(pattern2)
        if possible_files:
            output_path = possible_files[0]  # Use the first match
            logger.info(f"Found alternative output file: {output_path}")
        else:
            logger.error(f"No output file found for job {job_id}. Searched patterns: {pattern1}, {pattern2}")
            raise HTTPException(status_code=404, detail="Output file not found")
    
    # Create response with appropriate headers for PDF viewing
    response = FileResponse(
        output_path,
        media_type="application/pdf",
        filename=filename_prefix
    )
    
    # Add headers for better PDF viewing in iframe
    response.headers["Content-Disposition"] = "inline"  # View in browser instead of download
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache" 
    response.headers["Expires"] = "0"
    response.headers["ETag"] = f'"{job_id}-{int(time.time())}"'
    response.headers["X-Frame-Options"] = "SAMEORIGIN"  # Allow iframe from same origin
    response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
    
    return response

@router.get("/preview/{job_id}")
async def preview_result(job_id: str) -> FileResponse:
    """
    Preview processed document (optimized for iframe viewing)
    
    Args:
        job_id: Job identifier
        
    Returns:
        FileResponse with processed PDF optimized for preview
    """
    # Reuse the same logic as download but with different headers
    job_status = pii_processor.get_job_status(job_id)
    
    if job_status:
        if job_status["status"] != "completed":
            raise HTTPException(status_code=400, detail="Processing not completed")
        
        job = pii_processor.job_manager.get_job(job_id)
        if job and os.path.exists(job.output_path):
            output_path = job.output_path
        else:
            output_path = os.path.join(settings.OUTPUT_DIR, f"{job_id}_redacted.pdf")
    else:
        output_path = os.path.join(settings.OUTPUT_DIR, f"{job_id}_redacted.pdf")
    
    if not os.path.exists(output_path):
        # Try alternative filename patterns
        import glob
        pattern1 = os.path.join(settings.OUTPUT_DIR, f"{job_id}_*_redacted.pdf")
        pattern2 = os.path.join(settings.OUTPUT_DIR, f"{job_id}*redacted.pdf")
        
        possible_files = glob.glob(pattern1) + glob.glob(pattern2)
        if possible_files:
            output_path = possible_files[0]
        else:
            raise HTTPException(status_code=404, detail="Output file not found")
    
    # Create response optimized for iframe preview
    response = FileResponse(
        output_path,
        media_type="application/pdf"
    )
    
    # Headers optimized for iframe viewing - FORCE inline display
    response.headers["Content-Disposition"] = "inline; filename=\"preview.pdf\""
    response.headers["X-Frame-Options"] = "ALLOWALL"  # Allow iframe from anywhere
    response.headers["Content-Security-Policy"] = "frame-ancestors *"  # Allow all origins
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Cache-Control"] = "no-cache"  # Don't cache for real-time updates
    
    return response

@router.get("/jobs")
async def list_jobs() -> Dict[str, Any]:
    """
    List all jobs (for debugging/admin purposes)
    
    Returns:
        Dictionary with job list
    """
    from ..models.job import processing_jobs
    import glob
    
    jobs = []
    for job_id, job in processing_jobs.items():
        jobs.append({
            "job_id": job.job_id,
            "filename": job.filename,
            "status": job.status.value,
            "progress": job.progress,
            "created_at": job.created_at,
            "completed_at": job.completed_at
        })
    
    # Also list actual files on disk
    upload_files = glob.glob(os.path.join(settings.UPLOAD_DIR, "*"))
    output_files = glob.glob(os.path.join(settings.OUTPUT_DIR, "*"))
    
    return {
        "jobs": jobs,
        "total_jobs": len(jobs),
        "files_on_disk": {
            "uploads": [os.path.basename(f) for f in upload_files],
            "outputs": [os.path.basename(f) for f in output_files]
        }
    }