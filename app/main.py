from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.routers import upload, summarize

app = FastAPI(
    title=settings.APP_NAME,
    description="Scalable FastAPI backend for processing and summarizing Indian District Court legal documents.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Register routers
app.include_router(upload.router)
app.include_router(summarize.router)


@app.get("/", tags=["Health Check"])
async def root():
    """
    Health check endpoint returning application status.
    """
    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "stage": "Stage 3 - Gemini LLM Summarization Pipeline",
        "docs": "/docs"
    }


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom exception handler for request validation errors to ensure clean JSON responses.
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"Invalid request data: {exc.errors()}"}
    )
