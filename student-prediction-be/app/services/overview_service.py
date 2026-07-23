import logging

from app.db.client import get_db

logger = logging.getLogger(__name__)

RECENT_LIMIT = 20


async def get_overview() -> dict:
    db = get_db()

    # --- Collect all assessed students (for stats + recentStudents) ---
    batch_students_pipeline = [
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
    batch_students = await db.batch_jobs.aggregate(batch_students_pipeline).to_list(length=None)

    chat_students_pipeline = [
        {"$match": {"assessment": {"$exists": True}}},
        {"$project": {
            "_id": 0,
            "id": "$_id",
            "name": {"$ifNull": ["$studentName", {"$cond": [{"$eq": ["$source", "form"]}, "Form Assessment", "Chat Assessment"]}]},
            "studentId": {"$ifNull": ["$studentId", "$_id"]},
            "statusLabel": "$assessment.statusLabel",
            "riskLevel": "$assessment.riskLevel",
            "assessedAt": "$assessed_at",
        }},
    ]
    chat_students = await db.conversations.aggregate(chat_students_pipeline).to_list(length=None)

    all_students = batch_students + chat_students

    # --- Stats ---
    total = len(all_students)
    low = sum(1 for s in all_students if s.get("riskLevel") == "low")
    medium = sum(1 for s in all_students if s.get("riskLevel") == "medium")
    high = sum(1 for s in all_students if s.get("riskLevel") == "high")

    # --- Recent students: top N by assessedAt ---
    recent_students = sorted(
        [s for s in all_students if s.get("assessedAt")],
        key=lambda s: s["assessedAt"],
        reverse=True,
    )[:RECENT_LIMIT]

    # --- Recent sessions ---
    # Batch jobs (all statuses)
    batch_jobs = await db.batch_jobs.find({}).sort("created_at", -1).to_list(length=50)
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

    # Chat conversations (all, include in-progress)
    chat_convs = await db.conversations.find({}).sort("created_at", -1).to_list(length=50)
    chat_sessions = [
        {
            "id": conv["_id"],
            "type": "form" if conv.get("source") == "form" else "chat",
            "label": "Form Assessment" if conv.get("source") == "form" else "Chat Assessment",
            "createdAt": conv.get("created_at", ""),
            "status": "done" if conv.get("assessment") else "in_progress",
            "studentCount": None,
            "riskLevel": conv["assessment"].get("riskLevel") if conv.get("assessment") else None,
        }
        for conv in chat_convs
        if conv.get("created_at")
    ]

    recent_sessions = sorted(
        batch_sessions + chat_sessions,
        key=lambda s: s["createdAt"],
        reverse=True,
    )[:RECENT_LIMIT]

    logger.debug(
        "📊 [OVERVIEW] total=%d low=%d medium=%d high=%d sessions=%d students=%d",
        total, low, medium, high, len(recent_sessions), len(recent_students),
    )

    return {
        "totalAssessed": total,
        "lowRisk": low,
        "mediumRisk": medium,
        "highRisk": high,
        "recentSessions": recent_sessions,
        "recentStudents": recent_students,
    }
