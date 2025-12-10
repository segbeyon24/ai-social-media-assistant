import os
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

from app.auth_supabase import verify_supabase_jwt
from app.db import db

router = APIRouter()

YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
YOUTUBE_REDIRECT_URI = os.getenv("YOUTUBE_REDIRECT_URI")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
]

def get_flow():
    return Flow(
        client_type="web",
        client_config={
            "web": {
                "client_id": YOUTUBE_CLIENT_ID,
                "client_secret": YOUTUBE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [YOUTUBE_REDIRECT_URI]
            }
        },
        scopes=SCOPES,
        redirect_uri=YOUTUBE_REDIRECT_URI
    )


# ----------------------------------------------------
# STEP 1: Redirect user to Google OAuth screen
# ----------------------------------------------------
@router.get("/authorize")
async def youtube_authorize(jwt=Depends(verify_supabase_jwt)):
    flow = get_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    return {"auth_url": auth_url}


# ----------------------------------------------------
# STEP 2: OAuth Callback
# ----------------------------------------------------
@router.get("/callback")
async def youtube_callback(request: Request, jwt=Depends(verify_supabase_jwt)):
    user_id = jwt.get("sub")

    code = request.query_params.get("code")
    if not code:
        raise HTTPException(400, "Authorization code missing.")

    flow = get_flow()
    flow.fetch_token(code=code)

    creds = flow.credentials

    # Store or update YouTube tokens
    await db.execute("""
        INSERT INTO social_accounts (user_id, platform, access_token, refresh_token, meta)
        VALUES (:uid, 'youtube', :access, :refresh, :meta)
        ON CONFLICT (user_id, platform)
        DO UPDATE SET
            access_token = EXCLUDED.access_token,
            refresh_token = EXCLUDED.refresh_token,
            meta = EXCLUDED.meta
    """, {
        "uid": user_id,
        "access": creds.token,
        "refresh": creds.refresh_token,
        "meta": {"expires_in": creds.expiry.isoformat() if creds.expiry else None}
    })

    return RedirectResponse("/connected?platform=youtube")
