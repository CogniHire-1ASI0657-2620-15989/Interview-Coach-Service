from contextlib import asynccontextmanager
from secrets import compare_digest

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.infrastructure.configuration.settings import get_settings
from app.interfaces.rest.controller.interview_session_controller import router as interview_sessions_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_settings()
    yield


app = FastAPI(
    title="Interview Coach Service",
    description="Runs contextual interview-practice sessions for PathBridge candidates.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(interview_sessions_router)


@app.middleware("http")
async def require_internal_api_key(request: Request, call_next):
    if request.url.path == "/health":
        return await call_next(request)
    if not compare_digest(request.headers.get("X-Internal-Api-Key", ""), get_settings().internal_api_key):
        return JSONResponse(status_code=401, content={"detail": "Unauthorized service request."})
    return await call_next(request)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"service": "interview-coach", "status": "healthy"}
