"""
Job Manager Service for handling processing jobs
"""

import datetime
import logging
from typing import Dict, Optional

from ..models.job import ProcessingJob, processing_jobs, JobStatus

logger = logging.getLogger(__name__)

class JobManagerService:
    """Service for managing processing jobs"""
    
    def __init__(self):
        logger.info("Job Manager Service initialized")
    
    def create_job(self, filename: str, input_path: str, output_path: str) -> ProcessingJob:
        """
        Create a new processing job
        
        Args:
            filename: Original filename
            input_path: Path to input file
            output_path: Path for output file
            
        Returns:
            ProcessingJob instance
        """
        job = ProcessingJob.create_new(filename, input_path, output_path)
        processing_jobs[job.job_id] = job
        
        logger.info(f"Created job {job.job_id} for file {filename}")
        return job
    
    def get_job(self, job_id: str) -> Optional[ProcessingJob]:
        """
        Get job by ID
        
        Args:
            job_id: Job identifier
            
        Returns:
            ProcessingJob instance or None
        """
        return processing_jobs.get(job_id)
    
    def update_job_progress(self, job_id: str, progress: int, message: str = ""):
        """
        Update job progress
        
        Args:
            job_id: Job identifier
            progress: Progress percentage (0-100)
            message: Status message
        """
        if job_id in processing_jobs:
            processing_jobs[job_id].update_progress(progress, message)
            logger.debug(f"Job {job_id}: {progress}% - {message}")
    
    def add_job_log(self, job_id: str, log_entry: str):
        """
        Add log entry to job
        
        Args:
            job_id: Job identifier
            log_entry: Log message
        """
        if job_id in processing_jobs:
            processing_jobs[job_id].add_log(log_entry)
    
    def mark_job_completed(self, job_id: str, results: Dict):
        """
        Mark job as completed
        
        Args:
            job_id: Job identifier
            results: Processing results
        """
        if job_id in processing_jobs:
            processing_jobs[job_id].mark_completed(results)
            logger.info(f"Job {job_id} completed successfully")
    
    def mark_job_failed(self, job_id: str, error_message: str):
        """
        Mark job as failed
        
        Args:
            job_id: Job identifier
            error_message: Error description
        """
        if job_id in processing_jobs:
            processing_jobs[job_id].mark_failed(error_message)
            logger.error(f"Job {job_id} failed: {error_message}")
    
    def get_job_status_dict(self, job_id: str) -> Dict:
        """
        Get job status as dictionary for API response
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status dictionary
        """
        job = self.get_job(job_id)
        if not job:
            return None
        
        return {
            "job_id": job.job_id,
            "filename": job.filename,
            "status": job.status.value,
            "progress": job.progress,
            "message": job.message,
            "created_at": job.created_at,
            "completed_at": job.completed_at,
            "logs": job.logs,
            "results": job.results
        }
    
    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """
        Clean up jobs older than specified hours
        
        Args:
            max_age_hours: Maximum age in hours
        """
        current_time = datetime.datetime.now()
        cutoff_time = current_time - datetime.timedelta(hours=max_age_hours)
        
        jobs_to_remove = []
        for job_id, job in processing_jobs.items():
            job_time = datetime.datetime.fromisoformat(job.created_at)
            if job_time < cutoff_time:
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del processing_jobs[job_id]
            logger.info(f"Cleaned up old job {job_id}")
        
        if jobs_to_remove:
            logger.info(f"Cleaned up {len(jobs_to_remove)} old jobs")
