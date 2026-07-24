from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

_client: AsyncIOMotorClient | None = None

def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        # Báo lỗi nhanh để giao diện không phải chờ mặc định 30 giây khi MongoDB chưa chạy.
        _client = AsyncIOMotorClient(
            os.getenv("MONGODB_URL", "mongodb://localhost:27017"),
            serverSelectionTimeoutMS=2000,
            connectTimeoutMS=2000,
        )
    return _client

def get_db():
    return get_client()["student_risk_db"]
