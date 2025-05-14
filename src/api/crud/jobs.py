from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.models import ProcessingJob
from core.schemas import job as job_schemas


async def create_job(
    db: AsyncSession, job: job_schemas.ProcessingJobCreate
) -> ProcessingJob:
    """Create a new processing job in the database."""
    db_job = ProcessingJob(**job.model_dump())
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)
    return db_job


async def update_job(
    db: AsyncSession, job_id: str, update: job_schemas.ProcessingJobUpdate
) -> ProcessingJob:
    """Update an existing processing job in the database."""
    stmt = select(ProcessingJob).where(ProcessingJob.id == job_id)
    result = await db.execute(stmt)
    db_job = result.scalar_one()

    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(db_job, key, value)

    await db.commit()
    await db.refresh(db_job)
    return db_job


async def get_job_by_id(db: AsyncSession, job_id: str) -> ProcessingJob | None:
    """Retrieve a processing job by its ID."""
    stmt = select(ProcessingJob).where(ProcessingJob.id == job_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_all_jobs(db: AsyncSession) -> list[ProcessingJob]:
    """Retrieve all processing jobs from the database."""
    stmt = select(ProcessingJob).order_by(ProcessingJob.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_job_by_object_id(
    db: AsyncSession, object_id: str
) -> ProcessingJob | None:
    """Retrieve a processing job by its object ID."""
    stmt = select(ProcessingJob).where(ProcessingJob.object_id == object_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_job_by_creator_and_file(
    db: AsyncSession, created_by: str, file_name: str
) -> ProcessingJob | None:
    """Retrieve a processing job by creator and file name."""
    stmt = select(ProcessingJob).where(
        ProcessingJob.created_by == created_by,
        ProcessingJob.file_name == file_name,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
