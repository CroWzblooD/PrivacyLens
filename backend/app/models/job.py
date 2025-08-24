"""
Job models for processing tasks
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
import datetime
import uuid

class JobStatus(Enum):
    """Job processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class DetectionResult:
    """PII detection result"""
    text: str
    category: str
    coordinates: List[float]
    confidence: float
    method: str
    page_num: int = 0
    pattern_index: Optional[int] = None
    image_type: Optional[str] = None
    dimensions: Optional[str] = None

@dataclass
class ProcessingStats:
    """Processing statistics"""
    raw_text_extractions: int = 0
    pattern_matches: int = 0
    coordinate_searches: int = 0
    validation_checks: int = 0
    successful_detections: int = 0
    rejected_detections: int = 0
    image_analysis_attempts: int = 0
    successful_image_detections: int = 0
    redaction_applications: int = 0
    overlap_detections: int = 0
    overlap_preventions: int = 0
    smart_merges: int = 0
    rejected_oversized: int = 0

@dataclass
class ProcessingJob:
    """Processing job model"""
    job_id: str
    filename: str
    status: JobStatus
    progress: int = 0
    message: str = ""
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    completed_at: Optional[str] = None
    logs: List[str] = field(default_factory=list)
    input_path: str = ""
    output_path: str = ""
    results: Optional[Dict[str, Any]] = None
    stats: ProcessingStats = field(default_factory=ProcessingStats)
    
    @classmethod
    def create_new(cls, filename: str, input_path: str, output_path: str) -> 'ProcessingJob':
        """Create a new processing job"""
        job_id = str(uuid.uuid4())
        return cls(
            job_id=job_id,
            filename=filename,
            status=JobStatus.PENDING,
            input_path=input_path,
            output_path=output_path,
            message="Job created successfully"
        )
    
    def update_progress(self, progress: int, message: str = ""):
        """Update job progress"""
        self.progress = progress
        if message:
            self.message = message
    
    def add_log(self, log_entry: str):
        """Add log entry"""
        self.logs.append(log_entry)
    
    def mark_completed(self, results: Dict[str, Any]):
        """Mark job as completed"""
        self.status = JobStatus.COMPLETED
        self.progress = 100
        self.message = "Processing completed successfully"
        self.completed_at = datetime.datetime.now().isoformat()
        self.results = results
    
    def mark_failed(self, error_message: str):
        """Mark job as failed"""
        self.status = JobStatus.FAILED
        self.progress = 0
        self.message = f"Processing failed: {error_message}"
        self.completed_at = datetime.datetime.now().isoformat()

# Global job storage (in production, use a proper database)
processing_jobs: Dict[str, ProcessingJob] = {}