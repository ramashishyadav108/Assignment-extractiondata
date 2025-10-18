from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import logging
from pathlib import Path
import shutil

from app.models.schemas import UploadResponse, JobStatus
from app.services.job_manager import JobManager
from app.config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize job manager with absolute path
job_manager = JobManager(settings.PROJECT_ROOT / "jobs" if hasattr(settings, 'PROJECT_ROOT') else Path("jobs").resolve())


@router.post("/upload", response_model=UploadResponse)
async def upload_files(
    files: List[UploadFile] = File(...),
    template_id: str = Form(...)
):
    """
    Upload PDF files for extraction.
    
    Args:
        files: List of PDF files
        template_id: Template to use for extraction
        
    Returns:
        Upload response with job ID
    """
    try:
        # Validate template
        if template_id not in ["template_1", "template_2"]:
            raise HTTPException(status_code=400, detail="Invalid template ID")
        
        # Validate files
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        validated_files = []
        for file in files:
            # Check file extension
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type: {file.filename}. Only PDF files are allowed."
                )
            
            # Save file
            file_path = settings.UPLOAD_DIR / f"{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            validated_files.append(file.filename)
            logger.info(f"Saved file: {file_path}")
        
        # Create job
        job_id = job_manager.create_job(
            files_count=len(validated_files),
            template_id=template_id,
            file_names=validated_files
        )
        
        # Start processing in background using enhanced extraction
        from app.api.enhanced_extraction import process_enhanced_extraction_job
        import asyncio
        asyncio.create_task(process_enhanced_extraction_job(job_id, validated_files, template_id))
        
        return UploadResponse(
            job_id=job_id,
            status=JobStatus.PROCESSING,
            files_count=len(validated_files),
            message=f"Processing {len(validated_files)} file(s)"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
