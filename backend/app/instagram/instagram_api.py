"""
Instagram API Integration for AI Social Manager v0.3

Assumes:
- Token stored encrypted in user_social_tokens
- User has an Instagram Business Account linked to a Facebook Page

Exposes:
- Get IG Business Account
- Get posts
- Get reels
- Get comments
- Get insights
"""

import os
import httpx
from fastapi import APIRouter, Depends, HTTPException
from cryptography.fernet import Fernet
from .auth_supabase import verify_supabase_jwt
from .db import db

router = APIRouter()

FERNET_KEY = os.getenv("FERNET_KEY")
fernet = Fernet(FERNET_KEY.encode())


# --------------------------- Helper: Fetch Token ---------------------------

async def get_token(user_id: str):
    row = await db.fetch_one(
        "SELECT encrypted_token FROM user_social_tokens WHERE user_id = :uid AND platform = 'instagram'",
        {"uid": user_id}
    )
    if not row:
        raise HTTPException(400, "Instagram not connected")

    try:
        return fernet.decrypt(row["encrypted_token"].encode()).decode()
    except:
        raise HTTPException(500, "Token decryption failed")


# --------------------------- Helper: Fetch IG Business Account ---------------------------

async def get_business_account(token: str):
    """
    Step 1: Get Facebook Pages linked to user
    Step 2: Get Instagram Business Account ID
    """
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://graph.facebook.com/v18.0/me/accounts",
            params={"access_token": token},
        )

    data = r.json()
    pages = data.get("data", [])

    if not pages:
        raise HTTPException(400, "No Facebook pages found for this user")

    # Look for IG connected account
    for page in pages:
        page_id = page["id"]

        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"https://graph.facebook.com/v18.0/{page_id}",
                params={"fields": "instagram_business_account", "access_token": token},
            )

        obj = r.json()
        ig_acc = obj.get("instagram_business_account", {})
        if ig_acc.get("id"):
            return ig_acc["id"]

    raise HTTPException(400, "No Instagram Business Account connected")


# --------------------------- ROUTES ---------------------------

@router.get("/me")
async def me(jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    token = await get_token(user_id)
    ig_id = await get_business_account(token)
    return {"instagram_business_account_id": ig_id}


@router.get("/posts")
async def get_posts(jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    token = await get_token(user_id)
    ig_id = await get_business_account(token)

    url = f"https://graph.facebook.com/v18.0/{ig_id}/media"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, params={"access_token": token})

    return r.json()


@router.get("/reels")
async def get_reels(jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    token = await get_token(user_id)
    ig_id = await get_business_account(token)

    url = f"https://graph.facebook.com/v18.0/{ig_id}/media"
    params = {
        "fields": "media_type,media_url,thumbnail_url,timestamp,username,caption",
        "access_token": token,
    }

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)

    # Only return reels
    data = r.json()
    reels = [m for m in data.get("data", []) if m.get("media_type") == "VIDEO"]
    return {"reels": reels}


@router.get("/comments")
async def get_comments(post_id: str, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    token = await get_token(user_id)

    url = f"https://graph.facebook.com/v18.0/{post_id}/comments"
    params = {"access_token": token}

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)

    return r.json()


@router.get("/insights")
async def insights(post_id: str, jwt_payload=Depends(verify_supabase_jwt)):
    """
    Get insights for one post:
    - impressions
    - reach
    - engagement
    """
    user_id = jwt_payload.get("sub")
    token = await get_token(user_id)

    url = f"https://graph.facebook.com/v18.0/{post_id}/insights"
    params = {
        "metric": "impressions,reach,engagement",
        "access_token": token,
    }

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)

    return r.json()
