from pathlib import Path
from typing import Optional, Literal
from fastapi import APIRouter, File, UploadFile, Query, HTTPException, status, Depends
from app.services.auth import get_current_user, CurrentUser
from app.config import settings
from app.schemas.upload import DocumentResponse, ChunkDetail, ErrorDetail
from app.services.parser import parse_pdf, parse_docx
from app.services.cleaner import clean_legal_text
from app.services.chunking import chunk_document
from app.utils.token_estimator import estimate_tokens

router = APIRouter(tags=["Document Processing"])


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload, parse, clean, and chunk a legal document",
    description="Accepts a PDF or DOCX file (up to 100 MB), cleans text boilerplate, chunks it using specified strategy, and returns detailed chunk metadata.",
    responses={
        400: {"model": ErrorDetail, "description": "Bad Request (invalid extension, file empty, file size limit exceeded, encrypted/corrupted document)"},
        500: {"model": ErrorDetail, "description": "Internal server error during document processing"}
    }
)
async def upload_document(
    file: UploadFile = File(...),
    strategy: Literal["paragraph", "page", "merged"] = Query(
        default=settings.DEFAULT_CHUNK_STRATEGY,
        description="Chunking strategy to apply ('paragraph', 'page', or 'merged')"
    ),
    max_tokens: int = Query(
        default=settings.DEFAULT_MAX_TOKENS,
        ge=100,
        le=8000,
        description="Maximum estimated tokens per chunk"
    ),
    overlap: int = Query(
        default=settings.DEFAULT_CHUNK_OVERLAP,
        ge=0,
        le=500,
        description="Token overlap between adjacent chunks"
    ),
    current_user: CurrentUser = Depends(get_current_user)
) -> DocumentResponse:
    """
    Handles file upload, text extraction, legal text cleaning, and chunking.
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
            text, pages, page_texts = parse_pdf(contents)
        elif file_ext == ".docx":
            text, pages, page_texts = parse_docx(contents)
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while parsing the document."
        )

    cleaned_text = clean_legal_text(text)
    raw_chunks = chunk_document(
        text=text,
        pages_text=page_texts,
        strategy=strategy,
        max_tokens=max_tokens,
        overlap=overlap
    )

    chunk_objects = [
        ChunkDetail(
            chunk_index=idx,
            text=chunk_str,
            token_estimate=estimate_tokens(chunk_str)
        )
        for idx, chunk_str in enumerate(raw_chunks)
    ]

    return DocumentResponse(
        filename=file.filename,
        pages=pages,
        text=text,
        cleaned_text=cleaned_text,
        strategy_used=strategy,
        total_chunks=len(chunk_objects),
        chunks=chunk_objects
    )
