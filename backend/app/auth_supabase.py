"""
Supabase JWT verifier dependency for FastAPI.
- Verifies JWT using the SUPABASE_JWT_SECRET (service role key) from env
- Returns the decoded JWT payload (dict) for downstream handlers

Security note: Using service role key to verify tokens is acceptable for server-side verification
but keep the key private (not exposed to frontend). Supabase also exposes JWKS but service role is simple
for our environment.
"""
import os
from fastapi import HTTPException, Header
import jwt

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
if not SUPABASE_JWT_SECRET:
    raise RuntimeError("SUPABASE_JWT_SECRET env var must be set for JWT verification")


def verify_supabase_jwt(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"], options={"verify_aud": False})
        # Supabase tokens include "sub" (user id) and "email" for most accounts
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
