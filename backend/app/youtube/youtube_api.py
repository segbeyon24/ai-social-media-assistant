# youtube_api.py
"""
YouTube API helpers and analytics endpoints.
Provides endpoints to fetch:
- channel stats
- uploaded videos (list)
- liked videos (user's 'likes' playlist)
- comments for a video
- basic analytics/insights summary

Depends on tokens stored in social_accounts (provider='youtube'), encrypted with Fernet.
"""
import os
import time
import httpx
from fastapi import APIRouter, Depends, HTTPException
from cryptography.fernet import Fernet
from .db import db
from .auth_supabase import verify_supabase_jwt

router = APIRouter(prefix="/youtube", tags=["YouTube"])
FERNET_KEY = os.getenv('FERNET_KEY')
if not FERNET_KEY:
    raise RuntimeError('FERNET_KEY not set')
fernet = Fernet(FERNET_KEY.encode())

# Helper: get decrypted token for user
async def _get_tokens_for_user(user_id: str):
    row = await db.fetch_one('SELECT access_token, refresh_token, provider_user_id FROM social_accounts WHERE user_id = :uid AND provider = :prov', values={'uid': user_id, 'prov': 'youtube'})
    if not row:
        raise HTTPException(status_code=404, detail='youtube not connected')
    access = row['access_token']
    refresh = row['refresh_token']
    provider_user_id = row['provider_user_id']
    try:
        access = fernet.decrypt(access.encode()).decode() if access else None
        refresh = fernet.decrypt(refresh.encode()).decode() if refresh else None
    except Exception:
        raise HTTPException(status_code=500, detail='failed to decrypt token')
    return access, refresh, provider_user_id


@router.get('/stats')
async def channel_stats(jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get('sub')
    access, refresh, channel_id = await _get_tokens_for_user(user_id)

    # fetch channel details
    async with httpx.AsyncClient() as client:
        r = await client.get('https://www.googleapis.com/youtube/v3/channels', params={'part': 'snippet,statistics,contentDetails', 'id': channel_id, 'access_token': access})
        if r.status_code != 200:
            raise HTTPException(status_code=400, detail=f'failed to fetch channel: {r.text}')
        data = r.json()

    return data


@router.get('/uploads')
async def list_uploads(jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get('sub')
    access, refresh, channel_id = await _get_tokens_for_user(user_id)

    # get uploads playlist id
    async with httpx.AsyncClient() as client:
        ch = await client.get('https://www.googleapis.com/youtube/v3/channels', params={'part': 'contentDetails', 'id': channel_id, 'access_token': access})
        ch.raise_for_status()
        items = ch.json().get('items', [])
        uploads_pid = items[0]['contentDetails']['relatedPlaylists']['uploads']

        videos = []
        page_token = None
        while True:
            params = {'part': 'snippet,contentDetails', 'playlistId': uploads_pid, 'maxResults': 50}
            if page_token:
                params['pageToken'] = page_token
            r = await client.get('https://www.googleapis.com/youtube/v3/playlistItems', params={**params, 'access_token': access})
            r.raise_for_status()
            payload = r.json()
            for it in payload.get('items', []):
                videos.append(it)
            page_token = payload.get('nextPageToken')
            if not page_token:
                break

    return {'videos': videos}


@router.get('/likes')
async def liked_videos(jwt_payload=Depends(verify_supabase_jwt)):
    """List liked videos. Note: likes may be private depending on user settings."""
    user_id = jwt_payload.get('sub')
    access, refresh, channel_id = await _get_tokens_for_user(user_id)

    # The "Likes" playlist is a special playlist id: 'LL' is the liked videos for the authenticated user via playlistItems? Use 'myRating=like' as alternate.
    async with httpx.AsyncClient() as client:
        videos = []
        page_token = None
        while True:
            params = {'part': 'snippet,contentDetails', 'maxResults': 50, 'myRating': 'like'}
            if page_token:
                params['pageToken'] = page_token
            r = await client.get('https://www.googleapis.com/youtube/v3/videos', params={**params, 'access_token': access})
            r.raise_for_status()
            payload = r.json()
            for it in payload.get('items', []):
                videos.append(it)
            page_token = payload.get('nextPageToken')
            if not page_token:
                break

    return {'liked_videos': videos}


@router.get('/comments/{video_id}')
async def comments_for_video(video_id: str, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get('sub')
    access, refresh, channel_id = await _get_tokens_for_user(user_id)

    async with httpx.AsyncClient() as client:
        comments = []
        page_token = None
        while True:
            params = {'part': 'snippet', 'videoId': video_id, 'maxResults': 100}
            if page_token:
                params['pageToken'] = page_token
            r = await client.get('https://www.googleapis.com/youtube/v3/commentThreads', params={**params, 'access_token': access})
            r.raise_for_status()
            payload = r.json()
            comments.extend(payload.get('items', []))
            page_token = payload.get('nextPageToken')
            if not page_token:
                break
    return {'comments': comments}


@router.get('/insights')
async def basic_insights(jwt_payload=Depends(verify_supabase_jwt)):
    """Return simple analytics: total uploads, total likes on recent videos, avg views"""
    user_id = jwt_payload.get('sub')
    access, refresh, channel_id = await _get_tokens_for_user(user_id)

    # get uploads
    uploads_resp = await list_uploads(jwt_payload)
    videos = uploads_resp.get('videos', [])
    total = len(videos)
    views = 0
    likes = 0
    for v in videos[:50]:
        # fetch stats for each video
        vid_id = v['contentDetails']['videoId']
        async with httpx.AsyncClient() as client:
            r = await client.get('https://www.googleapis.com/youtube/v3/videos', params={'part': 'statistics', 'id': vid_id, 'access_token': access})
            if r.status_code != 200:
                continue
            stats = r.json().get('items', [])[0].get('statistics', {})
            views += int(stats.get('viewCount', 0))
            likes += int(stats.get('likeCount', 0))

    avg_views = views / total if total else 0
    return {'total_uploads': total, 'avg_views_recent': avg_views, 'likes_recent': likes}
