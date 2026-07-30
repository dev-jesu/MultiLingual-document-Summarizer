from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from app.config import settings
from app.schemas.upload import DocumentResponse, ErrorDetail
from app.services.parser import parse_pdf, parse_docx

router = APIRouter(tags=["Document Parsing"])


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload and extract text from a legal document",
    description="Accepts a PDF or DOCX file (up to 100 MB), validates and parses it, and returns extracted text.",
    responses={
        400: {"model": ErrorDetail, "description": "Bad Request (invalid extension, file empty, file size limit exceeded, encrypted/corrupted document)"},
        500: {"model": ErrorDetail, "description": "Internal server error during document processing"}
    }
)
async def upload_document(file: UploadFile = File(...)) -> DocumentResponse:
    """
    Handles file upload, input validation, and text extraction for PDF and DOCX documents.
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

    try:
        if file_ext == ".pdf":
            text, pages = parse_pdf(contents)
        elif file_ext == ".docx":
            text, pages = parse_docx(contents)
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
    except Exception:
        # Hide unhandled internal stack traces from clients
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while parsing the document."
        )

    return DocumentResponse(
        filename=file.filename,
        pages=pages,
        text=text
    )
