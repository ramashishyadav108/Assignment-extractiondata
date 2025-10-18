from fastapi import APIRouter, HTTPException
from pathlib import Path
import logging
from typing import Dict, Any, List

from app.services.job_manager import JobManager
from app.config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize job manager
job_manager = JobManager(settings.PROJECT_ROOT / "jobs")


@router.get("/results/{job_id}")
async def get_extraction_results(job_id: str) -> Dict[str, Any]:
    """
    Get the extracted data for a completed job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Extracted data in JSON format
    """
    try:
        job_data = job_manager.get_job(job_id)
        
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job_data['status'] != 'completed':
            raise HTTPException(
                status_code=400,
                detail=f"Job is not completed. Current status: {job_data['status']}"
            )
        
        extracted_data = job_data.get('extracted_data', [])
        
        if not extracted_data:
            raise HTTPException(status_code=404, detail="No extracted data found")
        
        return {
            'job_id': job_id,
            'template_id': job_data.get('template_id'),
            'files_count': job_data.get('files_count'),
            'extracted_data': extracted_data,
            'created_at': job_data.get('created_at'),
            'completed_at': job_data.get('completed_at')
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
