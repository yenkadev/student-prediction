import logging
from fastapi import APIRouter, HTTPException
from app.services import student_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/students/{student_id}")
async def get_student(student_id: str):
    try:
        data = await student_service.get_student(student_id)
        if data is None:
            raise HTTPException(status_code=404, detail=f"Student {student_id!r} not found")
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Student %s load error", student_id)
        raise HTTPException(status_code=500, detail=str(e))
