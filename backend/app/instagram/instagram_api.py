# app/instagram/instagram_api.py
"""
Instagram API helpers built on top of instagrapi sessions stored encrypted in social_accounts.access_token.
Provides endpoints to:
- list posts
- get post details (comments, likes)
- publish photo/video
- internal helper `publish_now_internal` used by main.py scheduled publisher

Note: instagrapi must be installed. This file uses Client.import_settings to restore session.
"""
import os
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from instagrapi import Client
from app.auth_supabase import verify_supabase_jwt
from app.db import db
from app.utils.crypto import encrypt, decrypt

router = APIRouter()

async def _load_client_from_user(user_id: str):
    row = await db.fetch_one("SELECT access_token, provider_user_id FROM social_accounts WHERE user_id = :u AND provider = 'instagram'", values={"u": user_id})
    if not row:
        raise HTTPException(404, "instagram not connected")
    enc = row['access_token']
    try:
        sess = decrypt(enc)
    except Exception as e:
        raise HTTPException(500, f'session decrypt failed: {e}')
    c = Client()
    # instagrapi expects dict-like settings; we eval (careful)
    try:
        settings = eval(sess)
    except Exception as e:
        raise HTTPException(500, f'invalid session blob: {e}')
    c.set_settings_dict(settings)
    try:
        c.login_by_session(settings)
    except Exception:
        # fallback: import settings
        try:
            c.set_settings_dict(settings)
            c.relogin()
        except Exception as e2:
            raise HTTPException(500, f'failed to restore session: {e2}')
    return c

@router.get('/me')
async def me(jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get('sub')
    row = await db.fetch_one("SELECT provider_user_id FROM social_accounts WHERE user_id = :u AND provider = 'instagram'", values={"u": user_id})
    if not row:
        raise HTTPException(404, 'not connected')
    return {"provider_user_id": row['provider_user_id']}

@router.get('/posts')
async def list_posts(jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get('sub')
    c = await _load_client_from_user(user_id)
    medias = c.user_medias(c.user_id, 50)
    result = []
    for m in medias:
        result.append({
            'id': m.pk,
            'media_type': m.media_type,
            'caption': m.caption,
            'like_count': m.like_count,
            'comment_count': m.comment_count,
            'taken_at': m.taken_at.isoformat() if m.taken_at else None,
        })
    return {'posts': result}

@router.get('/post/{post_id}')
async def get_post(post_id: int, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get('sub')
    c = await _load_client_from_user(user_id)
    m = c.media_info(post_id)
    return {'id': m.pk, 'caption': m.caption, 'comments': [com.dict() for com in c.media_comments(m.pk, 50)]}

@router.post('/publish')
async def publish_photo(media_url: str, caption: Optional[str] = None, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get('sub')
    c = await _load_client_from_user(user_id)
    # download and upload handled by instagrapi via URL
    try:
        res = c.photo_upload_url(media_url, caption or '')
    except Exception as e:
        raise HTTPException(500, f'publish failed: {e}')
    # store post
    await db.execute("INSERT INTO posts (user_id, platform, platform_post_id, content, created_at) VALUES (:u,'instagram',:pp,:c,NOW())", values={"u": user_id, "pp": str(res), "c": caption or ''})
    return {'platform_post_id': str(res)}

# internal helper used by main.publish_now and scheduled jobs
async def publish_now_internal(account_row, content: str, media: Optional[List[str]], access_token_blob: Optional[str] = None):
    # account_row is the full social_accounts row
    # access_token_blob if provided is the encrypted session
    enc = account_row.get('access_token') or access_token_blob
    if not enc:
        raise HTTPException(401, 'no session')
    try:
        sess = decrypt(enc)
    except Exception as e:
        raise HTTPException(500, f'session decrypt: {e}')
    c = Client()
    settings = eval(sess)
    c.set_settings_dict(settings)
    try:
        c.login_by_session(settings)
    except Exception:
        try:
            c.relogin()
        except Exception as e:
            raise HTTPException(500, f'relogin failed: {e}')
    if not media or len(media)==0:
        raise HTTPException(400, 'media required for IG publish')
    media_url = media[0]
    res = c.photo_upload_url(media_url, content or '')
    return {'platform_post_id': str(res)}
