"""Orchestrator agent for async-style audit job lifecycle management (MVP, in-memory)."""

from __future__ import annotations

import logging
from datetime import datetime
from enum import Enum
from typing import Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from src.agents.auditor.models import InputPayload
from src.agents.guards import DataQualityGuard
from src.agents.strategist import ChiefConsultantAgent, ExecutiveConsultingReport

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Lifecycle states for orchestrated audit jobs."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REJECTED_BY_GUARD = "REJECTED_BY_GUARD"


class JobRecord(BaseModel):
    """In-memory record of a single audit job."""

    job_id: str = Field(..., description="Unique job id (UUID)")
    status: JobStatus = Field(..., description="Current lifecycle state")
    created_at: datetime = Field(default_factory=datetime.now)
    result: Optional[ExecutiveConsultingReport] = Field(
        default=None,
        description="Executive report if the job completed successfully",
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error details for rejected/failed jobs",
    )


class Orchestrator:
    """Manages job submission, processing, and status retrieval."""

    def __init__(self) -> None:
        self._jobs: Dict[str, JobRecord] = {}
        self._guard = DataQualityGuard()

    def submit_job(self, payload: InputPayload) -> str:
        """
        Validate and enqueue a job in-memory.

        Returns:
            str: The generated job id.
        """
        job_id = str(uuid4())
        is_valid, errors = self._guard.validate_business_logic(payload)

        if not is_valid:
            record = JobRecord(
                job_id=job_id,
                status=JobStatus.REJECTED_BY_GUARD,
                error_message="; ".join(errors),
            )
            self._jobs[job_id] = record
            return job_id

        record = JobRecord(job_id=job_id, status=JobStatus.PENDING)
        self._jobs[job_id] = record
        return job_id

    def process_job(self, job_id: str, payload: InputPayload) -> None:
        """
        Execute a pending job and persist outcome to in-memory state.
        """
        job = self.get_job_status(job_id)
        job.status = JobStatus.RUNNING
        job.error_message = None

        try:
            consultant = ChiefConsultantAgent()
            report = consultant.generate_report(payload)
            job.result = report
            job.status = JobStatus.COMPLETED
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Job processing failed for job_id=%s", job_id)
            job.error_message = str(exc)
            job.status = JobStatus.FAILED

    def get_job_status(self, job_id: str) -> JobRecord:
        """Return current state of a job."""
        job = self._jobs.get(job_id)
        if job is None:
            raise KeyError(f"Job not found: {job_id}")
        return job
