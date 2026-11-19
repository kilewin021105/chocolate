import os
from supabase import create_client, Client

_client = None

def get_client():
    global _client
    if _client is not None:
        return _client

    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()

    if not url or not key or "YOUR_" in url or "YOUR_" in key:
        return None

    try:
        _client = create_client(url, key)
        return _client
    except Exception:
        return None
