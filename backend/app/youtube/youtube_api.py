import os
from fastapi import APIRouter, HTTPException, Depends
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

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
            "https://www.googleapis.com/auth/youtube.readonly",
        ],
    )


@router.get("/analytics")
async def youtube_analytics(jwt=Depends(verify_supabase_jwt)):
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

    # Fetch uploads playlist
    channel = service.channels().list(
        part="contentDetails",
        mine=True
    ).execute()

    uploads_playlist = channel["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    videos = service.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=uploads_playlist,
        maxResults=50
    ).execute()

    video_ids = [v["contentDetails"]["videoId"] for v in videos["items"]]

    if not video_ids:
        return {"videos": []}

    stats = service.videos().list(
        part="statistics,snippet",
        id=",".join(video_ids)
    ).execute()

    return {"videos": stats["items"]}
