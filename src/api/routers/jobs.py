# api/routers/jobs.py

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import jobs as crud_jobs
from core.db import models
from core.schemas.job import ProcessingJobResponse
from core.utils.auth import get_current_user
from core.utils.database import get_db

router = APIRouter()


@router.get("/")
async def list_all_jobs(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[models.User, Depends(get_current_user)],
) -> list[ProcessingJobResponse]:
    """List all processing jobs."""
    jobs = await crud_jobs.get_all_jobs(db)
    return [
        ProcessingJobResponse.model_validate(job, from_attributes=True) for job in jobs
    ]


@router.get("/{job_id}")
async def get_job_by_id(
    job_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
) -> ProcessingJobResponse:
    """Retrieve a processing job by its ID."""
    job = await crud_jobs.get_job_by_id(db, job_id)
    if not job or (job.created_by != user.id and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Job not found")
    return ProcessingJobResponse.model_validate(job, from_attributes=True)


@router.get("/by-object/{object_id}")
async def get_job_by_object_id(
    object_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[models.User, Depends(get_current_user)],
) -> ProcessingJobResponse:
    """Retrieve a processing job by its object ID."""
    job = await crud_jobs.get_job_by_object_id(db, object_id)
    if not job or (job.created_by != user.id and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Job not found")
    return ProcessingJobResponse.model_validate(job, from_attributes=True)
