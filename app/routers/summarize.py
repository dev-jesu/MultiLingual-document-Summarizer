from pathlib import Path
from fastapi import APIRouter, File, Form, UploadFile, HTTPException, status, Depends
from app.config import settings
from app.services.auth import get_current_user, CurrentUser
from app.schemas.summary import SummaryResponse
from app.schemas.upload import ErrorDetail
from app.services.language_detection import MixedLanguageError, UnsupportedLanguageError, normalize_language_parameters
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
async def summarize_document(
    file: UploadFile = File(...),
    source_language: str = Form(default=settings.DEFAULT_SOURCE_LANGUAGE),
    target_language: str = Form(default=settings.DEFAULT_TARGET_LANGUAGE),
    current_user: CurrentUser = Depends(get_current_user)
) -> SummaryResponse:
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
            parsed_result = parse_pdf(contents)
            if len(parsed_result) == 2:
                raw_text, pages = parsed_result
            else:
                raw_text, pages, _ = parsed_result
        elif file_ext == ".docx":
            parsed_result = parse_docx(contents)
            if len(parsed_result) == 2:
                raw_text, pages = parsed_result
            else:
                raw_text, pages, _ = parsed_result
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

    try:
        normalized_source, normalized_target = normalize_language_parameters(source_language, target_language)
    except (UnsupportedLanguageError, ValueError) as exc:
        logger.warning(f"Invalid language parameters for {file.filename}: {exc}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    logger.info(
        "Summarization request for %s | source_language=%s | target_language=%s",
        file.filename,
        normalized_source,
        normalized_target,
    )

    # 2. Summarize Document
    try:
        result = SummaryService.summarize_document(
            filename=file.filename,
            raw_text=raw_text,
            pages=pages,
            source_language=normalized_source,
            target_language=normalized_target,
        )
        return SummaryResponse(**result)
    except MixedLanguageError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except UnsupportedLanguageError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
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
