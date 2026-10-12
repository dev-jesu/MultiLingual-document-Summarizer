"""
Local In-Memory Database with JSON Persistence
Replaces Supabase for authentication and data storage.
All data lives in-process and persists to local_db_state.json on disk.

Pre-seeded dummy accounts:
  admin   / Admin@123    (role: admin)
  adv001  / Adv@12345    (role: advocate)
  adv002  / Adv@67890    (role: advocate)
"""
import uuid
import hashlib
import hmac
import os
import binascii
import json
from pathlib import Path
from datetime import datetime, timezone

DB_FILE = Path(__file__).resolve().parent.parent.parent / "local_db_state.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(password: str) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 (stdlib, no external deps)."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)
    return salt.hex() + ":" + binascii.hexlify(dk).decode()


def verify_password(plain: str, stored: str) -> bool:
    """Verify a PBKDF2 hashed password."""
    try:
        salt_hex, dk_hex = stored.split(":")
        salt = bytes.fromhex(salt_hex)
        dk = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt, 260_000)
        return hmac.compare_digest(binascii.hexlify(dk).decode(), dk_hex)
    except Exception:
        return False


# ─── In-Memory Tables ─────────────────────────────────────────────────────────

USERS: dict[str, dict] = {}          # keyed by user id
_USERNAME_INDEX: dict[str, str] = {} # username -> user id
CASES: dict[str, dict] = {}          # keyed by case id
CASE_MEMBERS: dict[str, dict] = {}   # keyed by membership id
DOCUMENTS: dict[str, dict] = {}      # keyed by document id
CHUNKS: dict[str, dict] = {}         # keyed by chunk id
AI_RUNS: dict[str, dict] = {}        # keyed by run id


# ─── Persistence ──────────────────────────────────────────────────────────────

def _save_db():
    try:
        data = {
            "users": USERS,
            "username_index": _USERNAME_INDEX,
            "cases": CASES,
            "case_members": CASE_MEMBERS,
            "documents": DOCUMENTS,
            "chunks": CHUNKS,
            "ai_runs": AI_RUNS,
        }
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        pass


def _load_db():
    if not DB_FILE.exists():
        _seed_users()
        return

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        USERS.clear()
        USERS.update(data.get("users", {}))
        _USERNAME_INDEX.clear()
        _USERNAME_INDEX.update(data.get("username_index", {}))
        CASES.clear()
        CASES.update(data.get("cases", {}))
        CASE_MEMBERS.clear()
        CASE_MEMBERS.update(data.get("case_members", {}))
        DOCUMENTS.clear()
        DOCUMENTS.update(data.get("documents", {}))
        CHUNKS.clear()
        CHUNKS.update(data.get("chunks", {}))
        AI_RUNS.clear()
        AI_RUNS.update(data.get("ai_runs", {}))
        _ensure_seed_users()
    except Exception:
        _seed_users()


# ─── Users ────────────────────────────────────────────────────────────────────
# Schema: { id, username, email, full_name, hashed_password, role, created_at }

SEED_ACCOUNTS = [
    ("92bfca1a-25b0-4686-ab32-e6d3174fc8de", "admin",  "admin@ecourt.local",  "System Administrator",  "Admin@123",  "admin"),
    ("b53ea4d6-f189-4c29-868b-3e28e21d46c3", "adv001", "adv001@ecourt.local", "Advocate Ramesh Kumar", "Adv@12345",  "advocate"),
    ("6346c2b9-cd6e-467d-bcf2-713d7f7214db", "adv002", "adv002@ecourt.local", "Advocate Priya Singh",  "Adv@67890",  "advocate"),
]


def _ensure_seed_users():
    changed = False
    for uid, username, email, full_name, password, role in SEED_ACCOUNTS:
        if uid not in USERS and username not in _USERNAME_INDEX:
            _create_user(username, email, full_name, password, role, user_id=uid)
            changed = True
    if changed:
        _save_db()


def _seed_users():
    """Pre-seed dummy accounts with deterministic UUIDs."""
    for uid, username, email, full_name, password, role in SEED_ACCOUNTS:
        if uid not in USERS and username not in _USERNAME_INDEX:
            _create_user(username, email, full_name, password, role, user_id=uid)
    _save_db()


def _create_user(username: str, email: str, full_name: str, password: str, role: str, user_id: str | None = None) -> dict:
    uid = user_id or str(uuid.uuid4())
    user = {
        "id": uid,
        "username": username,
        "email": email,
        "full_name": full_name,
        "hashed_password": _hash(password),
        "role": role,
        "created_at": _now(),
    }
    USERS[uid] = user
    _USERNAME_INDEX[username] = uid
    return user


def get_user_by_username(username: str) -> dict | None:
    uid = _USERNAME_INDEX.get(username)
    return USERS.get(uid) if uid else None


def get_user_by_id(user_id: str) -> dict | None:
    return USERS.get(user_id)


def list_users(role: str | None = None) -> list[dict]:
    users = list(USERS.values())
    if role:
        users = [u for u in users if u["role"] == role]
    return [_safe_user(u) for u in users]


def create_user(username: str, email: str, full_name: str, password: str, role: str) -> dict:
    if username in _USERNAME_INDEX:
        raise ValueError(f"Username '{username}' already exists")
    user = _create_user(username, email, full_name, password, role)
    _save_db()
    return _safe_user(user)


def _safe_user(u: dict) -> dict:
    return {k: v for k, v in u.items() if k != "hashed_password"}


# ─── Cases ────────────────────────────────────────────────────────────────────
# Schema: { id, case_number, title, description, court, court_name, court_level, stage, judge, status, created_by, created_at }

def list_cases() -> list[dict]:
    return list(CASES.values())


def get_case(case_id: str) -> dict | None:
    return CASES.get(case_id)


def create_case(data: dict, created_by: str) -> dict:
    cid = data.get("id") or str(uuid.uuid4())
    case = {
        "id": cid,
        "case_number": data.get("case_number", f"CASE-{cid[:8].upper()}"),
        "title": data.get("title", data.get("case_number", "Untitled Case")),
        "description": data.get("description", ""),
        "court": data.get("court", data.get("court_name", "")),
        "court_name": data.get("court_name", data.get("court", "")),
        "court_level": data.get("court_level", ""),
        "stage": data.get("stage", ""),
        "judge": data.get("judge", ""),
        "status": data.get("status", "active"),
        "created_by": created_by,
        "created_at": _now(),
    }
    CASES[cid] = case
    _save_db()
    return case


def update_case(case_id: str, data: dict) -> dict | None:
    case = CASES.get(case_id)
    if not case:
        return None
    allowed = {"title", "description", "court", "court_name", "court_level", "stage", "judge", "status", "case_number"}
    for k, v in data.items():
        if k in allowed:
            case[k] = v
    _save_db()
    return case


def delete_case(case_id: str) -> bool:
    res = bool(CASES.pop(case_id, None))
    if res:
        _save_db()
    return res


# ─── Case Members ─────────────────────────────────────────────────────────────
# Schema: { id, case_id, user_id, role, enrolled_at }

def enroll_member(case_id: str, user_id: str, role: str = "advocate") -> dict:
    mid = str(uuid.uuid4())
    member = {
        "id": mid,
        "case_id": case_id,
        "user_id": user_id,
        "role": role,
        "enrolled_at": _now(),
    }
    CASE_MEMBERS[mid] = member
    _save_db()
    return member


def is_member(case_id: str, user_id: str) -> dict | None:
    for m in CASE_MEMBERS.values():
        if m["case_id"] == case_id and m["user_id"] == user_id:
            return m
    return None


def get_case_members(case_id: str) -> list[dict]:
    members = [m for m in CASE_MEMBERS.values() if m["case_id"] == case_id]
    result = []
    for m in members:
        user = get_user_by_id(m["user_id"])
        result.append({
            **m,
            "user": _safe_user(user) if user else None,
        })
    return result


def get_user_cases(user_id: str) -> list[dict]:
    """Return cases where the user is a member."""
    memberships = [m for m in CASE_MEMBERS.values() if m["user_id"] == user_id]
    result = []
    for m in memberships:
        case = CASES.get(m["case_id"])
        if case:
            result.append({**case, "user_role": m["role"]})
    return result


def remove_member(member_id: str) -> bool:
    res = bool(CASE_MEMBERS.pop(member_id, None))
    if res:
        _save_db()
    return res


def remove_member_by_user(case_id: str, user_id: str) -> bool:
    for mid, m in list(CASE_MEMBERS.items()):
        if m["case_id"] == case_id and m["user_id"] == user_id:
            CASE_MEMBERS.pop(mid)
            _save_db()
            return True
    return False


# ─── Documents ────────────────────────────────────────────────────────────────
# Schema: { id, case_id, file_name, file_type, file_size, storage_path,
#           processing_status, extracted_text, uploaded_by, created_at }

def create_document(data: dict) -> dict:
    did = data.get("id", str(uuid.uuid4()))
    doc = {
        "id": did,
        "case_id": data["case_id"],
        "file_name": data["file_name"],
        "file_type": data.get("file_type", ""),
        "file_size": data.get("file_size", 0),
        "storage_path": data.get("storage_path", ""),
        "processing_status": data.get("processing_status", "pending"),
        "extracted_text": data.get("extracted_text", ""),
        "uploaded_by": data.get("uploaded_by", ""),
        "created_at": _now(),
    }
    DOCUMENTS[did] = doc
    _save_db()
    return doc


def update_document(doc_id: str, data: dict) -> dict | None:
    doc = DOCUMENTS.get(doc_id)
    if not doc:
        return None
    doc.update(data)
    _save_db()
    return doc


def get_document(doc_id: str) -> dict | None:
    return DOCUMENTS.get(doc_id)


def get_case_documents(case_id: str) -> list[dict]:
    return [d for d in DOCUMENTS.values() if d["case_id"] == case_id]


def delete_document(doc_id: str) -> bool:
    res = bool(DOCUMENTS.pop(doc_id, None))
    if res:
        _save_db()
    return res


# ─── Document Chunks ─────────────────────────────────────────────────────────
# Schema: { id, document_id, chunk_index, content, estimated_tokens }

def create_chunk(document_id: str, chunk_index: int, content: str, estimated_tokens: int) -> dict:
    cid = str(uuid.uuid4())
    chunk = {
        "id": cid,
        "document_id": document_id,
        "chunk_index": chunk_index,
        "content": content,
        "estimated_tokens": estimated_tokens,
    }
    CHUNKS[cid] = chunk
    _save_db()
    return chunk


def get_document_chunks(document_id: str) -> list[dict]:
    return sorted(
        [c for c in CHUNKS.values() if c["document_id"] == document_id],
        key=lambda x: x["chunk_index"]
    )


def delete_document_chunks(document_id: str):
    to_delete = [cid for cid, c in CHUNKS.items() if c["document_id"] == document_id]
    for cid in to_delete:
        CHUNKS.pop(cid)
    if to_delete:
        _save_db()


# ─── AI Runs ─────────────────────────────────────────────────────────────────
# Schema: { id, case_id, document_id, user_id, summary, language, created_at }

def create_ai_run(case_id: str, document_id: str, user_id: str, summary: str, language: str) -> dict:
    rid = str(uuid.uuid4())
    run = {
        "id": rid,
        "case_id": case_id,
        "document_id": document_id,
        "user_id": user_id,
        "summary": summary,
        "language": language,
        "created_at": _now(),
    }
    AI_RUNS[rid] = run
    _save_db()
    return run


def get_case_ai_runs(case_id: str) -> list[dict]:
    return [r for r in AI_RUNS.values() if r["case_id"] == case_id]


# ─── Bootstrap ───────────────────────────────────────────────────────────────
_load_db()
