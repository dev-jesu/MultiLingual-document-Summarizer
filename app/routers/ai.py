"""
AI Router — Case-level AI summarization using local in-memory DB.
No Supabase. Enrolled advocates can summarize documents in their cases.
"""
from fastapi import APIRouter, HTTPException, Form, Depends

from app.services.auth import get_current_user, CurrentUser
from app.db import local_db as db
from app.services.summary_service import SummaryService
from app.utils.logger import logger
from app.config import settings

router = APIRouter(prefix="/cases", tags=["Case AI Workspace"])


@router.post("/{case_id}/ai/summarize")
async def summarize_case_document(
    case_id: str,
    document_id: str = Form(...),
    target_language: str = Form("en"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Run AI summarization on a document.
    - Admin: can summarize any document in any case.
    - Advocate (enrolled): can summarize documents in their enrolled cases.
    """
    # Authorization check
    if current_user.role != "admin":
        member = db.is_member(case_id, current_user.id)
        if not member or member["role"] not in ["owner", "advocate"]:
            raise HTTPException(status_code=403, detail="Not authorized to run AI on this case")

    # Fetch document
    document = db.get_document(document_id)
    if not document or document.get("case_id") != case_id:
        raise HTTPException(status_code=404, detail="Document not found in this case")

    raw_text = document.get("extracted_text")
    if not raw_text:
        raise HTTPException(status_code=400, detail="Document has no extracted text. It may still be processing.")

    # Run summarization
    try:
        result = SummaryService.summarize_document(
            filename=document["file_name"],
            raw_text=raw_text,
            pages=1,
            source_language="auto",
            target_language=target_language,
        )
        summary = result["summary"]

        # Record AI run
        run = db.create_ai_run(
            case_id=case_id,
            document_id=document_id,
            user_id=current_user.id,
            summary=summary,
            language=target_language,
        )

        return {
            "id": run["id"],
            "summary": summary,
            "language": target_language,
            "document_name": document["file_name"],
        }

    except Exception as e:
        logger.error(f"Summarization failed for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


@router.get("/{case_id}/ai")
async def get_ai_runs(case_id: str, current_user: CurrentUser = Depends(get_current_user)):
    """Get all AI summarization runs for a case."""
    if current_user.role != "admin":
        member = db.is_member(case_id, current_user.id)
        if not member:
            raise HTTPException(status_code=403, detail="Not authorized")

    runs = db.get_case_ai_runs(case_id)

    # Enrich with document file name
    enriched = []
    for run in runs:
        doc = db.get_document(run.get("document_id", ""))
        enriched.append({
            **run,
            "document_name": doc["file_name"] if doc else None,
        })
    return enriched
