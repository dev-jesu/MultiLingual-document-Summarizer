import logging
from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger(__name__)

def _is_valid_ascii(s: str) -> bool:
    if not s:
        return False
    try:
        s.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False

class SupabaseService:
    _client: Client | None = None
    _anon_client: Client | None = None

    @classmethod
    def get_client(cls) -> Client:
        if cls._client is None:
            if not settings.SUPABASE_URL:
                raise ValueError("SUPABASE_URL is not configured.")

            # Check if service role key is set and valid ASCII (not masked with bullet points)
            key_to_use = None
            if settings.SUPABASE_SERVICE_ROLE_KEY and _is_valid_ascii(settings.SUPABASE_SERVICE_ROLE_KEY):
                key_to_use = settings.SUPABASE_SERVICE_ROLE_KEY
            elif settings.SUPABASE_ANON_KEY and _is_valid_ascii(settings.SUPABASE_ANON_KEY):
                logger.warning("SUPABASE_SERVICE_ROLE_KEY is missing or contains masked characters. Falling back to SUPABASE_ANON_KEY.")
                key_to_use = settings.SUPABASE_ANON_KEY
            else:
                raise ValueError("Neither valid SUPABASE_SERVICE_ROLE_KEY nor SUPABASE_ANON_KEY is available.")

            cls._client = create_client(settings.SUPABASE_URL, key_to_use)
        return cls._client

    @classmethod
    def get_anon_client(cls) -> Client:
        if cls._anon_client is None:
            if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
                raise ValueError("SUPABASE_URL or SUPABASE_ANON_KEY is not set.")
            cls._anon_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        return cls._anon_client

def get_supabase() -> Client:
    return SupabaseService.get_client()

def get_anon_supabase() -> Client:
    return SupabaseService.get_anon_client()

