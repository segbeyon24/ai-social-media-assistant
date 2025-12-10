"""
Instagram OAuth (Facebook Login) for AI Social Manager v0.3

Flow:
1. User clicks OAuth URL → Facebook Login
2. User approves → redirects to backend /auth/instagram/callback
3. Exchange 'code' for short-lived access token
4. Exchange short-lived token → long-lived token (60 days)
5. Store token encrypted in user_social_tokens (supabase)
"""

import os
import httpx
from fastapi import APIRouter, Depends, HTTPException
from cryptography.fernet import Fernet
from .auth_supabase import verify_supabase_jwt
from .db import db

router = APIRouter()

INSTAGRAM_CLIENT_ID = os.getenv("INSTAGRAM_CLIENT_ID")
INSTAGRAM_CLIENT_SECRET = os.getenv("INSTAGRAM_CLIENT_SECRET")
INSTAGRAM_REDIRECT_URI = os.getenv("INSTAGRAM_REDIRECT_URI")

FERNET_KEY = os.getenv("FERNET_KEY")
fernet = Fernet(FERNET_KEY.encode())


# ------------------------------------------------------------
# STEP 1 — Generate Instagram OAuth URL
# ------------------------------------------------------------

@router.get("/login")
async def instagram_login(jwt_payload=Depends(verify_supabase_jwt)):
    oauth_url = (
        "https://www.facebook.com/v18.0/dialog/oauth"
        f"?client_id={INSTAGRAM_CLIENT_ID}"
        f"&redirect_uri={INSTAGRAM_REDIRECT_URI}"
        "&scope=instagram_basic,instagram_manage_insights,pages_show_list,pages_read_engagement"
        "&response_type=code"
    )
    return {"auth_url": oauth_url}


# ------------------------------------------------------------
# STEP 2 — OAuth Callback
# ------------------------------------------------------------

@router.get("/callback")
async def instagram_callback(code: str, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")

    # Exchange code → short-lived token
    token_url = (
        "https://graph.facebook.com/v18.0/oauth/access_token"
        f"?client_id={INSTAGRAM_CLIENT_ID}"
        f"&redirect_uri={INSTAGRAM_REDIRECT_URI}"
        f"&client_secret={INSTAGRAM_CLIENT_SECRET}"
        f"&code={code}"
    )

    async with httpx.AsyncClient() as client:
        r = await client.get(token_url)
        if r.status_code != 200:
            raise HTTPException(400, "Failed to exchange OAuth code")
        data = r.json()

    short_lived = data.get("access_token")
    if not short_lived:
        raise HTTPException(400, "No short-lived token returned")

    # Exchange short-lived → long-lived (valid 60 days)
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://graph.facebook.com/v18.0/oauth/access_token",
            params={
                "grant_type": "fb_exchange_token",
                "client_id": INSTAGRAM_CLIENT_ID,
                "client_secret": INSTAGRAM_CLIENT_SECRET,
                "fb_exchange_token": short_lived,
            },
        )
        if r.status_code != 200:
            raise HTTPException(400, "Failed to exchange for long-lived token")
        long_data = r.json()

    long_token = long_data.get("access_token")
    expires_in = long_data.get("expires_in", None)

    if not long_token:
        raise HTTPException(400, "Failed to obtain long-lived token")

    encrypted = fernet.encrypt(long_token.encode()).decode()

    # Save encrypted token in DB
    query = """
        INSERT INTO user_social_tokens (user_id, platform, encrypted_token)
        VALUES (:uid, 'instagram', :t)
        ON CONFLICT (user_id, platform)
        DO UPDATE SET encrypted_token = EXCLUDED.encrypted_token, updated_at = NOW()
    """

    await db.execute(query, {"uid": user_id, "t": encrypted})

    return {
        "status": "connected",
        "platform": "instagram",
        "expires_in": expires_in,
    }
