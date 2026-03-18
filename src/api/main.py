"""FastAPI entrypoint for asynchronous orchestrator job processing."""

from __future__ import annotations

from fastapi import BackgroundTasks, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.agents.auditor.models import InputPayload
from src.orchestration import JobRecord, JobStatus, Orchestrator

# Global orchestrator instance (in-memory job store for current process)
orchestrator = Orchestrator()

app = FastAPI(
    title="Karbon Salinimi Orchestrator API",
    description="Async FastAPI integration for enterprise orchestrator job lifecycle.",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/v1/jobs", status_code=status.HTTP_202_ACCEPTED)
def create_job(payload: InputPayload, background_tasks: BackgroundTasks) -> dict:
    """Submit a job and schedule background processing for accepted payloads."""
    job_id = orchestrator.submit_job(payload)
    job = orchestrator.get_job_status(job_id)

    if job.status == JobStatus.REJECTED_BY_GUARD:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=job.model_dump(mode="json"),
        )

    background_tasks.add_task(orchestrator.process_job, job_id, payload)
    return {
        "job_id": job_id,
        "status": "processing",
        "message": "Job added to queue.",
    }


@app.get("/api/v1/jobs/{job_id}", response_model=JobRecord)
def get_job(job_id: str) -> JobRecord:
    """Return the latest status/result for a previously submitted job."""
    try:
        return orchestrator.get_job_status(job_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}",
        ) from exc
