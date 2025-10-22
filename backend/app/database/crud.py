"""
CRUD operations for database models.
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from .models import (
    UploadedFile,
    ExtractionResult,
    ExtractionLog,
    JobStatus,
    JobStatusEnum,
    LogLevelEnum
)


class UploadedFileService:
    """Service for UploadedFile model operations."""
    
    @staticmethod
    def create(
        db: Session,
        filename: str,
        original_filename: str,
        file_path: str,
        file_size: int,
        mime_type: str = "application/pdf"
    ) -> UploadedFile:
        """Create a new uploaded file record."""
        db_file = UploadedFile(
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        return db_file
    
    @staticmethod
    def get_by_id(db: Session, file_id: int) -> Optional[UploadedFile]:
        """Get uploaded file by ID."""
        return db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    
    @staticmethod
    def get_by_filename(db: Session, filename: str) -> Optional[UploadedFile]:
        """Get uploaded file by filename."""
        return db.query(UploadedFile).filter(UploadedFile.filename == filename).first()
    
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "desc"
    ) -> List[UploadedFile]:
        """Get all uploaded files with pagination."""
        query = db.query(UploadedFile)
        if order_by == "desc":
            query = query.order_by(UploadedFile.upload_timestamp.desc())
        else:
            query = query.order_by(UploadedFile.upload_timestamp.asc())
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def delete(db: Session, file_id: int) -> bool:
        """Delete uploaded file record."""
        db_file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
        if db_file:
            db.delete(db_file)
            db.commit()
            return True
        return False


class ExtractionResultService:
    """Service for ExtractionResult model operations."""
    
    @staticmethod
    def create(
        db: Session,
        file_id: int,
        excel_filename: str,
        excel_path: str,
        extracted_data: Optional[Dict[str, Any]] = None,
        processing_time: Optional[float] = None,
        total_characters_extracted: Optional[int] = None,
        total_sheets_generated: Optional[int] = None,
        gemini_model_used: Optional[str] = None
    ) -> ExtractionResult:
        """Create a new extraction result record."""
        db_result = ExtractionResult(
            file_id=file_id,
            excel_filename=excel_filename,
            excel_path=excel_path,
            extracted_data=extracted_data,
            processing_time=processing_time,
            total_characters_extracted=total_characters_extracted,
            total_sheets_generated=total_sheets_generated,
            gemini_model_used=gemini_model_used
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        return db_result
    
    @staticmethod
    def get_by_file_id(db: Session, file_id: int) -> Optional[ExtractionResult]:
        """Get extraction result by file ID."""
        return db.query(ExtractionResult).filter(ExtractionResult.file_id == file_id).first()
    
    @staticmethod
    def get_by_id(db: Session, result_id: int) -> Optional[ExtractionResult]:
        """Get extraction result by ID."""
        return db.query(ExtractionResult).filter(ExtractionResult.id == result_id).first()
    
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[ExtractionResult]:
        """Get all extraction results with pagination."""
        return db.query(ExtractionResult).order_by(
            ExtractionResult.extraction_timestamp.desc()
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_extracted_data(
        db: Session,
        result_id: int,
        extracted_data: Dict[str, Any]
    ) -> Optional[ExtractionResult]:
        """Update extracted data for a result."""
        db_result = db.query(ExtractionResult).filter(ExtractionResult.id == result_id).first()
        if db_result:
            db_result.extracted_data = extracted_data
            db.commit()
            db.refresh(db_result)
        return db_result


class JobStatusService:
    """Service for JobStatus model operations."""
    
    @staticmethod
    def create(
        db: Session,
        file_id: int,
        job_id: Optional[str] = None
    ) -> JobStatus:
        """Create a new job status record."""
        if not job_id:
            job_id = str(uuid.uuid4())
        
        db_job = JobStatus(
            file_id=file_id,
            job_id=job_id,
            status=JobStatusEnum.PENDING,
            progress_percentage=0
        )
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        return db_job
    
    @staticmethod
    def get_by_job_id(db: Session, job_id: str) -> Optional[JobStatus]:
        """Get job status by job ID."""
        return db.query(JobStatus).filter(JobStatus.job_id == job_id).first()
    
    @staticmethod
    def get_by_file_id(db: Session, file_id: int) -> Optional[JobStatus]:
        """Get job status by file ID."""
        return db.query(JobStatus).filter(JobStatus.file_id == file_id).first()
    
    @staticmethod
    def update_status(
        db: Session,
        job_id: str,
        status: JobStatusEnum,
        current_step: Optional[str] = None,
        progress_percentage: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> Optional[JobStatus]:
        """Update job status."""
        db_job = db.query(JobStatus).filter(JobStatus.job_id == job_id).first()
        if db_job:
            db_job.status = status
            if current_step is not None:
                db_job.current_step = current_step
            if progress_percentage is not None:
                db_job.progress_percentage = progress_percentage
            if error_message is not None:
                db_job.error_message = error_message
            
            # Update timestamps
            if status == JobStatusEnum.PROCESSING and not db_job.started_at:
                db_job.started_at = datetime.utcnow()
            elif status in [JobStatusEnum.COMPLETED, JobStatusEnum.FAILED, JobStatusEnum.CANCELLED]:
                db_job.completed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(db_job)
        return db_job
    
    @staticmethod
    def increment_retry(db: Session, job_id: str) -> Optional[JobStatus]:
        """Increment retry count for a job."""
        db_job = db.query(JobStatus).filter(JobStatus.job_id == job_id).first()
        if db_job:
            db_job.retry_count += 1
            db.commit()
            db.refresh(db_job)
        return db_job
    
    @staticmethod
    def get_all(
        db: Session,
        status: Optional[JobStatusEnum] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[JobStatus]:
        """Get all job statuses with optional filtering."""
        query = db.query(JobStatus)
        if status:
            query = query.filter(JobStatus.status == status)
        return query.order_by(JobStatus.created_at.desc()).offset(skip).limit(limit).all()


class ExtractionLogService:
    """Service for ExtractionLog model operations."""
    
    @staticmethod
    def create(
        db: Session,
        file_id: int,
        message: str,
        log_level: LogLevelEnum = LogLevelEnum.INFO,
        step: Optional[str] = None,
        duration_ms: Optional[int] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> ExtractionLog:
        """Create a new extraction log record."""
        db_log = ExtractionLog(
            file_id=file_id,
            log_level=log_level,
            message=message,
            step=step,
            duration_ms=duration_ms,
            extra_data=extra_data
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log
    
    @staticmethod
    def get_by_file_id(
        db: Session,
        file_id: int,
        log_level: Optional[LogLevelEnum] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ExtractionLog]:
        """Get logs for a specific file."""
        query = db.query(ExtractionLog).filter(ExtractionLog.file_id == file_id)
        if log_level:
            query = query.filter(ExtractionLog.log_level == log_level)
        return query.order_by(ExtractionLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_all(
        db: Session,
        log_level: Optional[LogLevelEnum] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ExtractionLog]:
        """Get all logs with optional filtering."""
        query = db.query(ExtractionLog)
        if log_level:
            query = query.filter(ExtractionLog.log_level == log_level)
        return query.order_by(ExtractionLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def delete_by_file_id(db: Session, file_id: int) -> int:
        """Delete all logs for a specific file."""
        count = db.query(ExtractionLog).filter(ExtractionLog.file_id == file_id).delete()
        db.commit()
        return count
