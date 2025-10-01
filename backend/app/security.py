import os
from typing import Optional
from fastapi import Header, HTTPException

API_TOKEN = os.getenv("API_TOKEN", "")

def require_token(authorization: Optional[str] = Header(None)):

    if not API_TOKEN:
        return  # allow if not set (dev)
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")
