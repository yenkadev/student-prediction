import logging
from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError
from app.routes import batch, chat, form, overview, prediction, sessions, student

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(title="Student Risk Warning API")

app.add_middleware(
    CORSMiddleware,
    # Allow the two Vite addresses commonly used when running and testing locally.
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(batch.router)
app.include_router(form.router)
app.include_router(overview.router)
app.include_router(sessions.router)
app.include_router(student.router)
app.include_router(prediction.router)


@app.exception_handler(PyMongoError)
async def handle_database_error(_request: Request, _error: PyMongoError) -> JSONResponse:
    """Return a clear error for every API that depends on MongoDB."""
    return JSONResponse(
        status_code=503,
        content={
            "detail": (
                "MongoDB is not ready. Start MongoDB if you are using "
                "Overview, history, Chat or background batch jobs."
            )
        },
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
