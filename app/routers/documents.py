"""
Documents Router — Uses local in-memory DB & local file storage. No Supabase.
Advocates can view documents for cases they are enrolled in.
Only admins can upload/allocate documents.
"""
import uuid
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends

from app.config import settings
from app.services.auth import get_current_user, CurrentUser
from app.db import local_db as db
from app.services.parser import parse_pdf, parse_docx
from app.services.cleaner import clean_legal_text
from app.services.chunking import chunk_document
from app.utils.token_estimator import estimate_tokens
from app.utils.logger import logger

router = APIRouter(prefix="/cases", tags=["Case Documents"])


@router.get("/{case_id}/documents")
async def get_documents(case_id: str, current_user: CurrentUser = Depends(get_current_user)):
    """
    Get documents for a case.
    - Admin: view all documents in any case.
    - Advocate (enrolled): view all documents in their cases.
    - Others: 403.
    """
    if current_user.role != "admin":
        member = db.is_member(case_id, current_user.id)
        if not member:
            raise HTTPException(status_code=403, detail="Not authorized to view documents for this case")

    return db.get_case_documents(case_id)


@router.post("/{case_id}/documents")
async def upload_case_document(
    case_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    file: UploadFile = File(...),
):
    """
    Upload a document to a case.
    Only admin can upload/allocate documents.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins can allocate documents to cases.",
        )

    case = db.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file format.")

    contents = await file.read()
    doc_uuid = str(uuid.uuid4())

    # Save to local disk
    upload_dir = Path(settings.UPLOAD_DIRECTORY) / case_id / doc_uuid
    upload_dir.mkdir(parents=True, exist_ok=True)
    storage_path = str(upload_dir / file.filename)
    with open(storage_path, "wb") as f:
        f.write(contents)

    doc = db.create_document({
        "id": doc_uuid,
        "case_id": case_id,
        "uploaded_by": current_user.id,
        "file_name": file.filename,
        "storage_path": storage_path,
        "file_type": file_ext,
        "file_size": len(contents),
        "processing_status": "processing",
    })

    try:
        if file_ext == ".pdf":
            parsed = parse_pdf(contents)
        elif file_ext == ".docx":
            parsed = parse_docx(contents)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        text = parsed[0]
        page_texts = parsed[2] if len(parsed) > 2 else []
        cleaned_text = clean_legal_text(text)

        raw_chunks = chunk_document(
            text=text,
            pages_text=page_texts,
            strategy=settings.DEFAULT_CHUNK_STRATEGY,
            max_tokens=settings.DEFAULT_MAX_TOKENS,
            overlap=settings.DEFAULT_CHUNK_OVERLAP,
        )

        for idx, chunk_str in enumerate(raw_chunks):
            db.create_chunk(doc_uuid, idx, chunk_str, estimate_tokens(chunk_str))

        db.update_document(doc_uuid, {
            "processing_status": "completed",
            "extracted_text": cleaned_text,
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        db.update_document(doc_uuid, {"processing_status": "failed"})
        raise HTTPException(status_code=500, detail="Failed to process document")

    return db.get_document(doc_uuid)
