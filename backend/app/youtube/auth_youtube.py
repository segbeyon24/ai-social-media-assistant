# auth_youtube.py
# YouTube OAuth2 integration for AI Social Manager

import os
import httpx
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from .db import db
from cryptography.fernet import Fernet
from .auth_supabase import verify_supabase_jwt

router = APIRouter()

YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "YOUR_YT_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "YOUR_YT_CLIENT_SECRET")
YOUTUBE_REDIRECT_URI = os.getenv("YOUTUBE_REDIRECT_URI", "YOUR_YT_REDIRECT_URI")
FERNET_KEY = os.getenv("FERNET_KEY")
fernet = Fernet(FERNET_KEY.encode())

oauth_scope = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly"

@router.get("/auth/youtube/start")
async def youtube_oauth_start(jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    params = {
        "client_id": YOUTUBE_CLIENT_ID,
        "redirect_uri": YOUTUBE_REDIRECT_URI,
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
        "scope": oauth_scope,
        "state": user_id,
    }
    return RedirectResponse(url=f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}")


@router.get("/auth/youtube/callback")
async def youtube_oauth_callback(code: str, state: str):
    # state = user_id
    token_url = "https://oauth2.googleapis.com/token"

    data = {
        "code": code,
        "client_id": YOUTUBE_CLIENT_ID,
        "client_secret": YOUTUBE_CLIENT_SECRET,
        "redirect_uri": YOUTUBE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(token_url, data=data)
        if r.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for access token")
        tokens = r.json()

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=400, detail="No refresh token returned by Google (consent missing)")

    encrypted_refresh = fernet.encrypt(refresh_token.encode()).decode()

    # Store in social_accounts
    await db.execute(
        query="""
        INSERT INTO social_accounts (user_id, platform, access_token, refresh_token)
        VALUES (:uid, 'youtube', :at, :rt)
        ON CONFLICT (user_id, platform) DO UPDATE SET
          access_token = EXCLUDED.access_token,
          refresh_token = EXCLUDED.refresh_token
        """,
        values={"uid": state, "at": access_token, "rt": encrypted_refresh}
    )

    return RedirectResponse(url="/success")
