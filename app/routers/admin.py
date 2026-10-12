"""
Admin Router — Admin-only endpoints for managing cases, enrolling advocates,
and allocating documents to cases.
Uses local in-memory DB; no Supabase.
"""
import uuid
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.services.auth import get_current_user, CurrentUser, require_role
from app.db import local_db as db
from app.services.parser import parse_pdf, parse_docx
from app.services.cleaner import clean_legal_text
from app.services.chunking import chunk_document
from app.utils.token_estimator import estimate_tokens
from app.utils.logger import logger
from app.config import settings

router = APIRouter(prefix="/admin", tags=["Admin Panel"])


# ── Pydantic Models ──────────────────────────────────────────

class EnrollAdvocateRequest(BaseModel):
    advocate_id: str
    role: str = "advocate"


class CreateUserRequest(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    role: str = "advocate"


# ── Dashboard Stats ──────────────────────────────────────────

@router.get("/stats")
async def admin_stats(current_user: CurrentUser = Depends(require_role("admin"))):
    """Get admin dashboard statistics."""
    return {
        "total_cases": len(db.CASES),
        "total_advocates": len([u for u in db.USERS.values() if u["role"] == "advocate"]),
        "total_documents": len(db.DOCUMENTS),
        "total_ai_runs": len(db.AI_RUNS),
    }


# ── User Management ──────────────────────────────────────────

@router.get("/users")
async def list_all_users(current_user: CurrentUser = Depends(require_role("admin"))):
    """List all users in the system."""
    return db.list_users()


@router.get("/advocates")
async def list_advocates(current_user: CurrentUser = Depends(require_role("admin"))):
    """List all advocates in the system."""
    return db.list_users(role="advocate")


@router.post("/users")
async def create_user(payload: CreateUserRequest, current_user: CurrentUser = Depends(require_role("admin"))):
    """Admin creates a new user account."""
    try:
        user = db.create_user(
            username=payload.username,
            email=payload.email,
            full_name=payload.full_name,
            password=payload.password,
            role=payload.role,
        )
        return user
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/advocates/{advocate_id}/cases")
async def get_advocate_cases(advocate_id: str, current_user: CurrentUser = Depends(require_role("admin"))):
    """Get all cases an advocate is enrolled in."""
    return db.get_user_cases(advocate_id)


# ── Case Management ─────────────────────────────────────────

@router.get("/cases")
async def admin_list_cases(current_user: CurrentUser = Depends(require_role("admin"))):
    """List ALL cases with member & document counts."""
    cases = db.list_cases()
    result = []
    for case in cases:
        members = db.get_case_members(case["id"])
        docs = db.get_case_documents(case["id"])
        result.append({
            **case,
            "members": members,
            "member_count": len(members),
            "document_count": len(docs),
        })
    return result


@router.post("/cases")
async def admin_create_case(payload: Dict[str, Any], current_user: CurrentUser = Depends(require_role("admin"))):
    """Admin creates a new case."""
    case = db.create_case(payload, created_by=current_user.id)
    # Admin becomes the owner
    db.enroll_member(case["id"], current_user.id, role="owner")
    return case


@router.get("/cases/{case_id}")
async def admin_get_case(case_id: str, current_user: CurrentUser = Depends(require_role("admin"))):
    """Get full case details including members, documents, and AI runs."""
    case = db.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return {
        "case": case,
        "members": db.get_case_members(case_id),
        "documents": db.get_case_documents(case_id),
        "ai_runs": db.get_case_ai_runs(case_id),
    }


@router.put("/cases/{case_id}")
async def admin_update_case(case_id: str, payload: Dict[str, Any], current_user: CurrentUser = Depends(require_role("admin"))):
    """Update case details."""
    case = db.update_case(case_id, payload)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.delete("/cases/{case_id}")
async def admin_delete_case(case_id: str, current_user: CurrentUser = Depends(require_role("admin"))):
    """Delete a case and all associated data."""
    if not db.get_case(case_id):
        raise HTTPException(status_code=404, detail="Case not found")
    db.delete_case(case_id)
    return {"message": "Case deleted successfully"}


# ── Advocate Enrollment ─────────────────────────────────────

@router.post("/cases/{case_id}/enroll")
async def enroll_advocate(
    case_id: str,
    payload: EnrollAdvocateRequest,
    current_user: CurrentUser = Depends(require_role("admin"))
):
    """Enroll an advocate into a case."""
    case = db.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    user = db.get_user_by_id(payload.advocate_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.is_member(case_id, payload.advocate_id)
    if existing:
        raise HTTPException(status_code=409, detail="User already enrolled in this case")

    member = db.enroll_member(case_id, payload.advocate_id, role=payload.role)
    return {
        "message": f"Successfully enrolled {user.get('full_name', user['username'])} as {payload.role}",
        "enrollment": member,
    }


@router.delete("/cases/{case_id}/members/{member_id}")
async def remove_member(case_id: str, member_id: str, current_user: CurrentUser = Depends(require_role("admin"))):
    """Remove a member from a case."""
    db.remove_member(member_id)
    return {"message": "Member removed successfully"}


# ── Document Allocation ──────────────────────────────────────

@router.post("/cases/{case_id}/allocate-document")
async def allocate_document(
    case_id: str,
    current_user: CurrentUser = Depends(require_role("admin")),
    file: UploadFile = File(...),
):
    """
    Admin uploads and allocates a document to a specific case.
    Files are stored locally under uploads/<case_id>/<doc_uuid>/<filename>.
    """
    case = db.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file format. Only PDF and DOCX are allowed.")

    contents = await file.read()

    # Store file locally
    doc_uuid = str(uuid.uuid4())
    upload_dir = Path(settings.UPLOAD_DIRECTORY) / case_id / doc_uuid
    upload_dir.mkdir(parents=True, exist_ok=True)
    storage_path = str(upload_dir / file.filename)
    with open(storage_path, "wb") as f:
        f.write(contents)

    # Create document record
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

    # Run processing pipeline
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
        logger.info(f"Document '{file.filename}' allocated to case {case_id} successfully")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing failed for '{file.filename}': {e}")
        db.update_document(doc_uuid, {"processing_status": "failed"})
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

    return db.get_document(doc_uuid)


@router.delete("/cases/{case_id}/documents/{document_id}")
async def remove_document(case_id: str, document_id: str, current_user: CurrentUser = Depends(require_role("admin"))):
    """Remove a document from a case."""
    db.delete_document_chunks(document_id)
    db.delete_document(document_id)
    return {"message": "Document removed successfully"}
