import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat, batch, overview, sessions, student

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(title="Student Risk Warning API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(batch.router)
app.include_router(overview.router)
app.include_router(sessions.router)
app.include_router(student.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
