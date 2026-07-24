from fastapi import APIRouter, HTTPException
from app.schemas.form import FormRequest, FormResultResponse
from app.services import form_service

router = APIRouter()


@router.post("/predict/form", response_model=FormResultResponse)
async def predict_form(request: FormRequest) -> dict:
    try:
        return await form_service.process_form(
            fields=request.fields,
            prediction_type=request.predictionType,
            data_source=request.dataSource,
            name=request.name,
            student_id=request.studentId,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
