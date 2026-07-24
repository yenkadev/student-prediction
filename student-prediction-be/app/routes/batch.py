"""CSV/Excel upload API for both synchronous mode and background jobs."""

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, Response, UploadFile

from app.db.client import get_db
from app.schemas.batch import BatchJobResponse, BatchSubmitResponse, BatchSyncResponse
from app.services import batch_service, risk_service


router = APIRouter()
MAX_FILE_SIZE = 50 * 1024 * 1024


def _validate_upload(filename: str, file_bytes: bytes) -> None:
    """Validate the file format and size before analysis."""
    if not filename.lower().endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=422, detail="File must be in CSV or Excel format."
        )
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds the 50 MB limit.")


@router.post("/predict/batch/sync", response_model=BatchSyncResponse)
async def predict_batch_sync(
    file: UploadFile = File(...),
    dataSource: str = Form(...),
    predictionType: str = Form(...),
) -> BatchSyncResponse:
    """Analyze the file immediately; suitable for demos and testing without MongoDB."""
    filename = file.filename or "upload.csv"
    file_bytes = await file.read()
    _validate_upload(filename, file_bytes)
    try:
        risk_service.validate_selection(dataSource, predictionType)
        results = batch_service.assess_file(
            file_bytes, filename, dataSource, predictionType
        )
        return BatchSyncResponse(results=results)
    except (ValueError, RuntimeError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post("/predict/batch", response_model=BatchSubmitResponse)
async def submit_batch(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    dataSource: str = Form(...),
    predictionType: str = Form(...),
) -> BatchSubmitResponse:
    """Keep the background-job API for environments that have MongoDB."""
    filename = file.filename or "upload.csv"
    file_bytes = await file.read()
    _validate_upload(filename, file_bytes)
    try:
        job_id = await batch_service.create_job(predictionType, dataSource, filename)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    background_tasks.add_task(
        batch_service.process_job,
        job_id=job_id,
        file_bytes=file_bytes,
        filename=filename,
        prediction_type=predictionType,
        data_source=dataSource,
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


@router.delete("/predict/batch/{job_id}", status_code=204)
async def delete_batch_job(job_id: str) -> Response:
    result = await get_db().batch_jobs.delete_one({"_id": job_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return Response(status_code=204)
