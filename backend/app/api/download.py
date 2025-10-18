from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import logging

from app.services.job_manager import JobManager
from app.config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize job manager
job_manager = JobManager(settings.PROJECT_ROOT / "jobs")


@router.get("/download/{job_id}")
async def download_result(job_id: str):
    """
    Download the extracted Excel file for a completed job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Excel file download
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
        
        output_file = Path(job_data.get('output_file'))
        
        if not output_file.exists():
            raise HTTPException(status_code=404, detail="Output file not found")
        
        return FileResponse(
            path=str(output_file),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=output_file.name
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
