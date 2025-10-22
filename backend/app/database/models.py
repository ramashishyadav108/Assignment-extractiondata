"""
Database models for PDF extraction system.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class JobStatusEnum(str, enum.Enum):
    """Job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LogLevelEnum(str, enum.Enum):
    """Log level enumeration."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class UploadedFile(Base):
    """Model for uploaded PDF files."""
    
    __tablename__ = "uploaded_files"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    mime_type = Column(String(100), default="application/pdf")
    upload_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    extraction_result = relationship("ExtractionResult", back_populates="uploaded_file", uselist=False, cascade="all, delete-orphan")
    job_status = relationship("JobStatus", back_populates="uploaded_file", uselist=False, cascade="all, delete-orphan")
    logs = relationship("ExtractionLog", back_populates="uploaded_file", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<UploadedFile(id={self.id}, filename='{self.filename}')>"


class ExtractionResult(Base):
    """Model for storing extraction results."""
    
    __tablename__ = "extraction_results"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_id = Column(Integer, ForeignKey("uploaded_files.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Result data
    excel_filename = Column(String(255), nullable=False)
    excel_path = Column(String(512), nullable=False)
    extracted_data = Column(JSON, nullable=True)  # Store structured JSON data
    
    # Metadata
    extraction_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    processing_time = Column(Float, nullable=True)  # Time in seconds
    
    # Statistics
    total_characters_extracted = Column(Integer, nullable=True)
    total_sheets_generated = Column(Integer, nullable=True)
    gemini_model_used = Column(String(100), nullable=True)
    
    # Relationships
    uploaded_file = relationship("UploadedFile", back_populates="extraction_result")
    
    def __repr__(self):
        return f"<ExtractionResult(id={self.id}, file_id={self.file_id}, excel_filename='{self.excel_filename}')>"


class JobStatus(Base):
    """Model for tracking job status."""
    
    __tablename__ = "job_statuses"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_id = Column(Integer, ForeignKey("uploaded_files.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    job_id = Column(String(100), unique=True, nullable=False, index=True)  # UUID for job tracking
    
    # Status tracking
    status = Column(Enum(JobStatusEnum), default=JobStatusEnum.PENDING, nullable=False, index=True)
    current_step = Column(String(100), nullable=True)  # e.g., "uploading", "extracting_text", "processing_with_ai", "generating_excel"
    progress_percentage = Column(Integer, default=0, nullable=False)  # 0-100
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    uploaded_file = relationship("UploadedFile", back_populates="job_status")
    
    def __repr__(self):
        return f"<JobStatus(id={self.id}, job_id='{self.job_id}', status='{self.status}')>"


class ExtractionLog(Base):
    """Model for storing extraction process logs."""
    
    __tablename__ = "extraction_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_id = Column(Integer, ForeignKey("uploaded_files.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Log details
    log_level = Column(Enum(LogLevelEnum), default=LogLevelEnum.INFO, nullable=False, index=True)
    message = Column(Text, nullable=False)
    step = Column(String(100), nullable=True)  # Which step in the process
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    duration_ms = Column(Integer, nullable=True)  # Duration of the step in milliseconds
    
    # Additional context - renamed from 'metadata' to 'extra_data' to avoid SQLAlchemy conflict
    extra_data = Column(JSON, nullable=True)  # Any additional structured data
    
    # Relationships
    uploaded_file = relationship("UploadedFile", back_populates="logs")
    
    def __repr__(self):
        return f"<ExtractionLog(id={self.id}, file_id={self.file_id}, level='{self.log_level}', message='{self.message[:50]}...')>"
