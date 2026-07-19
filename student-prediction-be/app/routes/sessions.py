from fastapi import APIRouter
from app.db.client import get_db

router = APIRouter()


@router.get("/students")
async def get_all_students() -> dict:
    db = get_db()

    batch_pipeline = [
        {"$match": {"status": "done"}},
        {"$unwind": "$results"},
        {"$project": {
            "_id": 0,
            "id": "$results.id",
            "name": "$results.name",
            "studentId": "$results.studentId",
            "statusLabel": "$results.assessment.statusLabel",
            "riskLevel": "$results.assessment.riskLevel",
            "assessedAt": "$results.assessed_at",
        }},
    ]
    batch_students = await db.batch_jobs.aggregate(batch_pipeline).to_list(length=None)

    chat_pipeline = [
        {"$match": {"assessment": {"$exists": True}}},
        {"$project": {
            "_id": 0,
            "id": "$_id",
            "name": {"$ifNull": ["$studentName", "Chat Assessment"]},
            "studentId": {"$ifNull": ["$studentId", "$_id"]},
            "statusLabel": "$assessment.statusLabel",
            "riskLevel": "$assessment.riskLevel",
            "assessedAt": "$assessed_at",
        }},
    ]
    chat_students = await db.conversations.aggregate(chat_pipeline).to_list(length=None)

    all_students = sorted(
        [s for s in batch_students + chat_students if s.get("assessedAt")],
        key=lambda s: s["assessedAt"],
        reverse=True,
    )

    return {"students": all_students}


@router.get("/sessions")
async def get_all_sessions() -> dict:
    db = get_db()

    batch_jobs = await db.batch_jobs.find({}).sort("created_at", -1).to_list(length=None)
    batch_sessions = [
        {
            "id": job["_id"],
            "type": "batch",
            "label": job.get("filename", "Batch upload"),
            "createdAt": job.get("created_at", ""),
            "status": job.get("status", "failed"),
            "studentCount": len(job.get("results", [])),
            "riskLevel": None,
        }
        for job in batch_jobs
        if job.get("created_at")
    ]

    chat_convs = await db.conversations.find({}).sort("created_at", -1).to_list(length=None)
    chat_sessions = [
        {
            "id": conv["_id"],
            "type": "chat",
            "label": "Chat Assessment",
            "createdAt": conv.get("created_at", ""),
            "status": "done" if conv.get("assessment") else "in_progress",
            "studentCount": None,
            "riskLevel": conv["assessment"].get("riskLevel") if conv.get("assessment") else None,
        }
        for conv in chat_convs
        if conv.get("created_at")
    ]

    all_sessions = sorted(
        batch_sessions + chat_sessions,
        key=lambda s: s["createdAt"],
        reverse=True,
    )

    return {"sessions": all_sessions}
