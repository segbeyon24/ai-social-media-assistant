# app/instagram/auth_instagram.py
"""
Instagram integration using instagrapi (private API)
- Connect endpoint: user provides their IG username/password (or session exported blob)
- We login via instagrapi.Client and store exported settings encrypted in social_accounts.access_token

SECURITY NOTE: Storing credentials is sensitive. We encrypt with FERNET_KEY but recommend using per-user app passwords or instructing users to use OAuth-like flows for production.
"""
import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from instagrapi import Client
from app.auth_supabase import verify_supabase_jwt
from app.db import db
from app.utils.crypto import encrypt, decrypt

router = APIRouter()

class IGConnectIn(BaseModel):
    username: str
    password: str


@router.post('/connect')
async def connect_ig(payload: IGConnectIn, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get('sub')
    username = payload.username
    password = payload.password

    c = Client()
    try:
        c.login(username, password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'instagram login failed: {e}')

    # export settings (session) to persist login
    settings = c.get_settings_dict()
    session_blob = str(settings)
    enc = encrypt(session_blob)

    # store in social_accounts table
    await db.execute("INSERT INTO social_accounts (user_id, provider, provider_user_id, access_token, refresh_token, scopes, expires_at, created_at) VALUES (:u, 'instagram', :puid, :at, NULL, NULL, NULL, NOW()) ON CONFLICT (user_id, provider) DO UPDATE SET provider_user_id = EXCLUDED.provider_user_id, access_token = EXCLUDED.access_token", values={"u": user_id, "puid": username, "at": enc})

    return {"status": "connected", "provider_user_id": username}


@router.post('/disconnect')
async def disconnect_ig(jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get('sub')
    await db.execute("DELETE FROM social_accounts WHERE user_id = :u AND provider = 'instagram'", values={"u": user_id})
    return {"status": "disconnected"}
