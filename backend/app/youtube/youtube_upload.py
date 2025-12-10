import os
import googleapiclient.http
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.auth_supabase import verify_supabase_jwt
from app.db import db

router = APIRouter()


def get_creds(row):
    return Credentials(
        token=row["access_token"],
        refresh_token=row["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("YOUTUBE_CLIENT_ID"),
        client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
        scopes=[
            "https://www.googleapis.com/auth/youtube.upload",
        ],
    )


@router.post("/upload")
async def youtube_upload(
    title: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    jwt=Depends(verify_supabase_jwt)
):
    user_id = jwt.get("sub")

    row = await db.fetch_one("""
        SELECT access_token, refresh_token
        FROM social_accounts
        WHERE user_id = :uid AND platform = 'youtube'
    """, {"uid": user_id})

    if not row:
        raise HTTPException(404, "No YouTube account connected")

    creds = get_creds(row)
    service = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {"title": title, "description": description},
        "status": {"privacyStatus": "public"},
    }

    media = googleapiclient.http.MediaIoBaseUpload(
        file.file,
        mimetype=file.content_type,
        chunksize=1024 * 1024,
        resumable=True
    )

    upload = service.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    ).execute()

    return {"status": "uploaded", "video": upload}
