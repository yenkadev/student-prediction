from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, Form
from app.schemas.batch import BatchSubmitResponse, BatchJobResponse
from app.services import batch_service

router = APIRouter()


@router.post("/predict/batch", response_model=BatchSubmitResponse)
async def submit_batch(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    predictionType: str = Form(...),
) -> BatchSubmitResponse:
    if predictionType not in ("ml", "rule_based"):
        raise HTTPException(status_code=422, detail="predictionType must be 'ml' or 'rule_based'")

    filename = file.filename or "upload.csv"
    if not filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(status_code=422, detail="File must be CSV or Excel (.csv, .xlsx, .xls)")

    file_bytes = await file.read()
    if len(file_bytes) > 50 * 1024 * 1024:  # 50 MB
        raise HTTPException(status_code=413, detail="File too large (max 50 MB)")
    job_id = await batch_service.create_job(predictionType)

    background_tasks.add_task(
        batch_service.process_job,
        job_id=job_id,
        file_bytes=file_bytes,
        filename=filename,
        prediction_type=predictionType,
    )

    return BatchSubmitResponse(jobId=job_id)


@router.get("/predict/batch/{job_id}", response_model=BatchJobResponse)
async def get_batch_job(job_id: str) -> BatchJobResponse:
    job = await batch_service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return BatchJobResponse(
        status=job["status"],
        progress=job["progress"],
        results=job.get("results") if job["status"] == "done" else None,
        error=job.get("error"),
    )
