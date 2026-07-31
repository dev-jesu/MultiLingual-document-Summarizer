from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from app.config import settings
from app.schemas.summary import SummaryResponse
from app.schemas.upload import ErrorDetail
from app.services.parser import parse_pdf, parse_docx
from app.services.summary_service import SummaryService
from app.utils.logger import logger

router = APIRouter(tags=["Document Summarization"])

@router.post(
    "/summarize",
    response_model=SummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload and summarize a legal document",
    description="Accepts a PDF or DOCX file, extracts text, chunks it if necessary, and generates an English summary using the Gemini API.",
    responses={
        400: {"model": ErrorDetail, "description": "Bad Request (invalid extension, file empty, file size limit exceeded, encrypted/corrupted document)"},
        500: {"model": ErrorDetail, "description": "Internal server error during document processing or API failure"}
    }
)
async def summarize_document(file: UploadFile = File(...)) -> SummaryResponse:
    """
    Handles file upload, input validation, text extraction, and summarization pipeline.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing."
        )

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{file_ext}'. Only PDF (.pdf) and DOCX (.docx) files are accepted."
        )

    try:
        contents = await file.read()
    except Exception as e:
        logger.error(f"Failed to read upload {file.filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not read uploaded file: {str(e)}"
        )

    if not contents or len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    if len(contents) > settings.MAX_UPLOAD_SIZE:
        max_mb = settings.MAX_UPLOAD_SIZE // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed limit of {max_mb} MB."
        )

    # 1. Parse Document
    try:
        if file_ext == ".pdf":
            raw_text, pages = parse_pdf(contents)
        elif file_ext == ".docx":
            raw_text, pages = parse_docx(contents)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file format."
            )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as e:
        logger.error(f"Unexpected parsing error for {file.filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while parsing the document."
        )

    # 2. Summarize Document
    try:
        result = SummaryService.summarize_document(
            filename=file.filename,
            raw_text=raw_text,
            pages=pages
        )
        return SummaryResponse(**result)
    except ValueError as val_err:
        # Configuration error (e.g., missing API key)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(val_err)
        )
    except Exception as e:
        logger.error(f"Summarization pipeline failed for {file.filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during the summarization process. Please try again later."
        )
