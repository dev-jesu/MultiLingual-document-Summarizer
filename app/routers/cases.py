"""
Cases Router — Uses local in-memory DB. No Supabase.
- Admin sees ALL cases
- Advocates see only their enrolled cases
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from app.services.auth import get_current_user, CurrentUser
from app.db import local_db as db

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.get("/")
async def get_cases(current_user: CurrentUser = Depends(get_current_user)):
    """
    Get cases for the authenticated user.
    - Admin: sees ALL cases
    - Advocate: sees only enrolled cases
    """
    if current_user.role == "admin":
        cases = db.list_cases()
        for case in cases:
            members = db.get_case_members(case["id"])
            case["user_role"] = "admin"
            case["member_count"] = len(members)
            case["document_count"] = len(db.get_case_documents(case["id"]))
        return cases
    else:
        cases = db.get_user_cases(current_user.id)
        for case in cases:
            case["document_count"] = len(db.get_case_documents(case["id"]))
        return cases


@router.get("/{case_id}")
async def get_case(case_id: str, current_user: CurrentUser = Depends(get_current_user)):
    """Get case details. Admin can view any case; advocates can view enrolled cases only."""
    if current_user.role != "admin":
        member = db.is_member(case_id, current_user.id)
        if not member:
            raise HTTPException(status_code=403, detail="Not authorized to view this case")
        role = member["role"]
    else:
        role = "admin"

    case = db.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    members = db.get_case_members(case_id)
    documents = db.get_case_documents(case_id)

    return {
        "case": case,
        "user_role": role,
        "documents": documents,
        "members": members,
    }


@router.post("/")
async def create_case(payload: Dict[str, Any], current_user: CurrentUser = Depends(get_current_user)):
    """Create a new case. Only admins can create cases."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create cases.")
    case = db.create_case(payload, created_by=current_user.id)
    db.enroll_member(case["id"], current_user.id, role="owner")
    return case
