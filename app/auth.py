import os, hmac, hashlib, base64
from fastapi import Request, HTTPException

SECRET = os.environ.get("SESSION_SECRET", "dev-secret").encode()
PASSWORD = os.environ.get("APP_PASSWORD", "sportscar")

def _sign(value: str) -> str:
    sig = hmac.new(SECRET, value.encode(), hashlib.sha256).digest()
    return f"{value}|{base64.urlsafe_b64encode(sig).decode()}"

def _verify(signed: str) -> bool:
    try:
        value, sig_b64 = signed.split("|", 1)
        expect = hmac.new(SECRET, value.encode(), hashlib.sha256).digest()
        return hmac.compare_digest(base64.urlsafe_b64decode(sig_b64), expect)
    except Exception:
        return False

def new_session_cookie_value() -> str:
    return _sign("ok")

def require_login(request: Request):
    token = request.cookies.get("session")
    if not token or not _verify(token):
        raise HTTPException(status_code=401, detail="Unauthorized")
