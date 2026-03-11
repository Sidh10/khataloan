import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
from api.schemas import ProcessingStatus, CreditProfileResponse
from agents.orchestrator import run_pipeline

router = APIRouter()

# In-memory job store (use Redis in production)
jobs: dict = {}


@router.post("/upload", response_model=ProcessingStatus)
async def upload_artifacts(
    background_tasks: BackgroundTasks,
    ledger_images: List[UploadFile] = File(default=[]),
    voice_notes: List[UploadFile] = File(default=[]),
    upi_screenshots: List[UploadFile] = File(default=[]),
):
    """
    Upload financial artifacts for processing.
    Accepts any combination of ledger images, voice notes, and UPI screenshots.
    """
    if not ledger_images and not voice_notes and not upi_screenshots:
        raise HTTPException(status_code=400, detail="At least one file must be uploaded.")

    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "queued", "stage": "ingest", "progress": 0, "message": "Upload received"}

    # Read file bytes before passing to background task
    ledger_bytes   = [(f.filename, await f.read()) for f in ledger_images]
    voice_bytes    = [(f.filename, await f.read()) for f in voice_notes]
    upi_bytes      = [(f.filename, await f.read()) for f in upi_screenshots]

    background_tasks.add_task(run_pipeline, job_id, ledger_bytes, voice_bytes, upi_bytes, jobs)

    return ProcessingStatus(
        job_id=job_id,
        status="queued",
        stage="ingest",
        progress=0,
        message="Files received. Processing started.",
    )


@router.get("/status/{job_id}", response_model=ProcessingStatus)
def get_status(job_id: str):
    """Poll this endpoint to track processing progress."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found.")
    j = jobs[job_id]
    return ProcessingStatus(job_id=job_id, **j)


@router.get("/report/{job_id}", response_model=CreditProfileResponse)
def get_report(job_id: str):
    """Retrieve the completed credit profile report."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found.")
    j = jobs[job_id]
    if j["status"] != "complete":
        raise HTTPException(status_code=202, detail=f"Processing not complete. Status: {j['status']}")
    return j["result"]


@router.get("/report/{job_id}/pdf")
def download_pdf(job_id: str):
    """Download the generated PDF credit report."""
    if job_id not in jobs or jobs[job_id]["status"] != "complete":
        raise HTTPException(status_code=404, detail="Report not ready.")
    pdf_path = jobs[job_id].get("pdf_path")
    if not pdf_path:
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"khataloan_report_{job_id[:8]}.pdf")
