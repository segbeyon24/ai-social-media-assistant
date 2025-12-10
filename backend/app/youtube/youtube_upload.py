# youtube_upload.py
"""
YouTube Upload + Token Refresh Logic
-----------------------------------
Handles:
- Exchange auth code for tokens
- Refresh tokens when expired
- Upload videos to YouTube

Depends on:
- google_auth_oauthlib
- google_auth
- google-api-python-client

Environmental variables (placeholder names — replace in your .env):
- YT_CLIENT_ID
- YT_CLIENT_SECRET
- YT_REDIRECT_URI

Database tables required (see supabase_schema_youtube.sql canvas):
- youtube_tokens (user_id, access_token, refresh_token, expiry)
- youtube_uploads (user_id, video_id, title, description)
"""

import os
import datetime
import httpx
from fastapi import APIRouter, Depends, HTTPException
from .auth_supabase import verify_supabase_jwt
from .db import db

router = APIRouter(prefix="/youtube", tags=["YouTube"])

YT_CLIENT_ID = os.getenv("YT_CLIENT_ID")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET")
YT_REDIRECT_URI = os.getenv("YT_REDIRECT_URI")

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"

# ------------------------------
# TOKEN HELPERS
# ------------------------------

async def exchange_code_for_tokens(code: str):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            TOKEN_URL,
            data={
                "code": code,
                "client_id": YT_CLIENT_ID,
                "client_secret": YT_CLIENT_SECRET,
                "redirect_uri": YT_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        if r.status_code != 200:
            raise HTTPException(400, f"Failed to exchange code: {r.text}")
        return r.json()

async def refresh_access_token(refresh_token: str):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            TOKEN_URL,
            data={
                "refresh_token": refresh_token,
                "client_id": YT_CLIENT_ID,
                "client_secret": YT_CLIENT_SECRET,
                "grant_type": "refresh_token",
            },
        )
        if r.status_code != 200:
            raise HTTPException(400, f"Failed to refresh token: {r.text}")
        return r.json()

async def get_valid_access_token(user_id: str) -> str:
    row = await db.fetch_one(
        "SELECT access_token, refresh_token, expiry FROM youtube_tokens WHERE user_id = :uid",
        {"uid": user_id},
    )
    if not row:
        raise HTTPException(400, "User has not connected YouTube")

    access = row["access_token"]
    refresh = row["refresh_token"]
    expiry = row["expiry"]

    if expiry and expiry > datetime.datetime.utcnow():
        return access

    # --- refresh needed ---
    data = await refresh_access_token(refresh)
    new_access = data["access_token"]
    new_expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=data.get("expires_in", 3600))

    await db.execute(
        "UPDATE youtube_tokens SET access_token = :a, expiry = :e WHERE user_id = :u",
        {"a": new_access, "e": new_expiry, "u": user_id},
    )

    return new_access

# ------------------------------
# ROUTES
# ------------------------------

@router.post("/callback")
async def youtube_callback(data: dict, jwt_payload=Depends(verify_supabase_jwt)):
    """
    Frontend sends { "code": "..." } after Google redirects back.
    """
    user_id = jwt_payload.get("sub")
    code = data.get("code")
    if not code:
        raise HTTPException(400, "Missing authorization code")

    tokens = await exchange_code_for_tokens(code)

    access = tokens.get("access_token")
    refresh = tokens.get("refresh_token")
    expires_in = tokens.get("expires_in", 3600)
    expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)

    # Upsert
    q = """
    INSERT INTO youtube_tokens (user_id, access_token, refresh_token, expiry)
    VALUES (:uid, :a, :r, :e)
    ON CONFLICT (user_id) DO UPDATE SET
        access_token = EXCLUDED.access_token,
        refresh_token = EXCLUDED.refresh_token,
        expiry = EXCLUDED.expiry;
    """

    await db.execute(q, {"uid": user_id, "a": access, "r": refresh, "e": expiry})

    return {"status": "connected", "expires_in": expires_in}


@router.post("/upload")
async def youtube_upload(data: dict, jwt_payload=Depends(verify_supabase_jwt)):
    """
    Uploads a video to user's YouTube.
    data: { title, description, file_url }
    file_url = remote URL or frontend pre-uploaded blob.
    """

    user_id = jwt_payload.get("sub")

    title = data.get("title")
    description = data.get("description")
    file_url = data.get("file_url")

    if not file_url:
        raise HTTPException(400, "Missing file_url")

    # 1. Ensure access token
    access_token = await get_valid_access_token(user_id)

    # 2. Prepare metadata
    metadata = {
        "snippet": {
            "title": title or "Untitled Upload",
            "description": description or "",
        },
        "status": {"privacyStatus": "private"},
    }

    # 3. Start resumable upload
    async with httpx.AsyncClient() as client:
        init_res = await client.post(
            UPLOAD_URL,
            json=metadata,
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Upload-Content-Type": "video/*",
            },
        )

        if init_res.status_code not in (200, 201):
            raise HTTPException(400, f"Failed to init upload: {init_res.text}")

        upload_url = init_res.headers.get("Location")
        if not upload_url:
            raise HTTPException(400, "Missing upload URL from YouTube")

        # 4. Fetch bytes
        video_bytes = await client.get(file_url)
        if video_bytes.status_code != 200:
            raise HTTPException(400, "Failed to download video file")

        # 5. Upload bytes
        upload_res = await client.put(
            upload_url,
            content=video_bytes.content,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Length": str(len(video_bytes.content)),
            },
        )

        if upload_res.status_code not in (200, 201):
            raise HTTPException(400, f"Upload failed: {upload_res.text}")

        video_id = upload_res.json().get("id")

        # save history
        await db.execute(
            "INSERT INTO youtube_uploads (user_id, video_id, title, description) VALUES (:u, :v, :t, :d)",
            {"u": user_id, "v": video_id, "t": title, "d": description},
        )

        return {"status": "uploaded", "video_id": video_id}
