from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TemplateType(str, Enum):
    TEMPLATE_1 = "template_1"
    TEMPLATE_2 = "template_2"


class UploadRequest(BaseModel):
    template_id: TemplateType = Field(..., description="Template to use for extraction")


class UploadResponse(BaseModel):
    job_id: str
    status: JobStatus
    files_count: int
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: float = Field(..., ge=0, le=100)
    files_processed: int
    total_files: int
    errors: List[str] = []
    created_at: datetime
    completed_at: Optional[datetime] = None


class ExtractionResult(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    errors: List[str] = []
    confidence_score: Optional[float] = None


class TemplateField(BaseModel):
    name: str
    field: str
    type: str
    required: bool = False
    description: Optional[str] = None


class TemplateConfig(BaseModel):
    template_id: str
    name: str
    description: str
    columns: List[TemplateField]
    required_fields: List[str]


class ValidationResult(BaseModel):
    is_valid: bool
    issues: List[str] = []
    warnings: List[str] = []
