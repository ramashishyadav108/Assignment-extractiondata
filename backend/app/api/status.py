from fastapi import APIRouter, HTTPException
from pathlib import Path
import logging

from app.models.schemas import JobStatusResponse, JobStatus
from app.services.job_manager import JobManager
from app.config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize job manager
job_manager = JobManager(settings.PROJECT_ROOT / "jobs")


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status of an extraction job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Job status information
    """
    try:
        job_data = job_manager.get_job(job_id)
        
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return JobStatusResponse(
            job_id=job_data['job_id'],
            status=JobStatus(job_data['status']),
            progress=job_data['progress'],
            files_processed=job_data['files_processed'],
            total_files=job_data['files_count'],
            errors=job_data.get('errors', []),
            created_at=job_data['created_at'],
            completed_at=job_data.get('completed_at')
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
