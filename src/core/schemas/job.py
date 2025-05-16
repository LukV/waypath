# core/schemas/job.py

from datetime import datetime

from pydantic import BaseModel

from core.utils.config import ProcessingStatus


class ProcessingJobCreate(BaseModel):
    """Schema for creating a new processing job."""

    id: str
    file_name: str
    created_by: str
    status: ProcessingStatus = ProcessingStatus.PENDING


class ProcessingJobUpdate(BaseModel):
    """Schema for updating an existing processing job."""

    status: ProcessingStatus
    error_message: str | None = None


class ProcessingJobResponse(BaseModel):
    """Schema for returning processing job details."""

    id: str
    file_name: str | None
    status: ProcessingStatus
    error_message: str | None
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


class JobQueuedResponse(BaseModel):
    """Schema for returning job queued response."""

    job_id: str
    status: ProcessingStatus = ProcessingStatus.PROCESSING
