"""
app/main.py — Unified, complete, repo-ready main for AI Social Manager v0.5

Assumptions / notes:
- This file lives at /backend/app/main.py and uses absolute package imports (app.*).
- DB helper `db` exposes async methods: connect(), disconnect(), fetch_one(), fetch_all(), execute().
- auth_supabase.verify_supabase_jwt dependency returns the decoded token payload.
- instagram and youtube modules expose routers and *internal helper functions*:
    - app.instagram.instagram_api.publish_now_internal(account_row, content, media, access_token_blob=None)
    - app.youtube.youtube_upload.upload_from_url_internal(account_row, url, title)
  The code attempts to import these helpers; if missing the endpoints will raise a helpful error.
- APScheduler (AsyncIOScheduler) is used as an in-process scheduler (you chose APScheduler).
- Fernet key must be set in FERNET_KEY env var.
- Keep this file as the single source of truth for routes and scheduler wiring.
"""

import os
import asyncio
import datetime
import time
from typing import Optional, List, Any, Dict

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from cryptography.fernet import Fernet

# Scheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Core app modules (must exist)
from app.auth_supabase import verify_supabase_jwt
from app.db import db
from app.ai_adapter import generate_text

# Routers (instagram/youtube). Import routers and optionally internal helpers.
from app.instagram import auth_instagram as instagram_auth_module
from app.instagram import instagram_api as instagram_api_module

from app.youtube import auth_youtube as youtube_auth_module
from app.youtube import youtube_upload as youtube_upload_module
from app.youtube import youtube_api as youtube_api_module

# Try to resolve internal helper functions used by scheduler/publish-now
_publish_instagram_internal = getattr(instagram_api_module, "publish_now_internal", None)
_publish_youtube_internal = getattr(youtube_upload_module, "upload_from_url_internal", None)

# App initialization
app = FastAPI(title="AI Social Manager - Backend v0.5")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # narrow in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fernet encryption
FERNET_KEY = os.getenv("FERNET_KEY")
if not FERNET_KEY:
    raise RuntimeError("FERNET_KEY must be set in environment")

fernet = Fernet(FERNET_KEY.encode())

# Scheduler instance
scheduler = AsyncIOScheduler()

# Pydantic models
class StoreAIKeyIn(BaseModel):
    provider: str  # "openai" or "gemini"
    api_key: str

class GenerateIn(BaseModel):
    prompt: str
    model: Optional[str] = "gpt-4o-mini"

class ScheduleIn(BaseModel):
    social_account_id: str
    content: str
    scheduled_at: Optional[str] = None  # ISO string, optional (immediate if missing)
    metadata: Optional[Dict[str, Any]] = None

class PublishNowIn(BaseModel):
    social_account_id: str
    content: str
    media: Optional[List[str]] = None  # list of media URLs

# Include routers from modules (namespaced)
app.include_router(instagram_auth_module.router, prefix="/auth/instagram", tags=["instagram"])
app.include_router(instagram_api_module.router, prefix="/instagram", tags=["instagram"])

app.include_router(youtube_auth_module.router, prefix="/auth/youtube", tags=["youtube"])
app.include_router(youtube_upload_module.router, prefix="/youtube/upload", tags=["youtube"])
app.include_router(youtube_api_module.router, prefix="/youtube", tags=["youtube"])


# ---- Startup / Shutdown ----
@app.on_event("startup")
async def _startup():
    await db.connect()
    # Start scheduler and add job to publish scheduled posts every 60 seconds
    if not scheduler.running:
        scheduler.start()
    # Ensure job exists
    scheduler.add_job(func=run_scheduled_publisher, trigger=IntervalTrigger(seconds=60), id="scheduled_publisher", replace_existing=True)


@app.on_event("shutdown")
async def _shutdown():
    try:
        scheduler.shutdown(wait=False)
    except Exception:
        pass
    await db.disconnect()


# ---- Health ----
@app.get("/health")
async def health():
    return {"status": "ok", "ts": int(time.time())}


# ---- AI keys endpoints ----
@app.post("/user/ai-key")
async def store_ai_key(payload: StoreAIKeyIn, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="unauthenticated")
    provider = payload.provider.lower()
    if provider not in ("openai", "gemini"):
        raise HTTPException(status_code=400, detail="provider must be 'openai' or 'gemini'")

    encrypted = fernet.encrypt(payload.api_key.encode()).decode()
    query = """
        INSERT INTO user_api_keys (user_id, provider, encrypted_api_key, created_at)
        VALUES (:uid, :prov, :enc, NOW())
        ON CONFLICT (user_id, provider) DO UPDATE
            SET encrypted_api_key = EXCLUDED.encrypted_api_key,
                created_at = NOW()
    """
    await db.execute(query=query, values={"uid": user_id, "prov": provider, "enc": encrypted})
    return {"status": "ok", "provider": provider}


@app.get("/user/ai-key")
async def list_ai_keys(jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    rows = await db.fetch_all("SELECT provider, created_at FROM user_api_keys WHERE user_id = :uid", values={"uid": user_id})
    return {"keys": [dict(r) for r in rows]}


@app.delete("/user/ai-key/{provider}")
async def delete_ai_key(provider: str, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    await db.execute("DELETE FROM user_api_keys WHERE user_id = :uid AND provider = :prov", values={"uid": user_id, "prov": provider.lower()})
    return {"status": "deleted", "provider": provider.lower()}


# ---- AI generate (primary OpenAI, failover Gemini) ----
@app.post("/ai/generate")
async def ai_generate(payload: GenerateIn, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    # fetch keys
    row_open = await db.fetch_one("SELECT encrypted_api_key FROM user_api_keys WHERE user_id = :uid AND provider = 'openai'", values={"uid": user_id})
    row_gem = await db.fetch_one("SELECT encrypted_api_key FROM user_api_keys WHERE user_id = :uid AND provider = 'gemini'", values={"uid": user_id})
    openai_key = None
    gemini_key = None
    if row_open and row_open.get("encrypted_api_key"):
        try:
            openai_key = fernet.decrypt(row_open["encrypted_api_key"].encode()).decode()
        except Exception:
            openai_key = None
    if row_gem and row_gem.get("encrypted_api_key"):
        try:
            gemini_key = fernet.decrypt(row_gem["encrypted_api_key"].encode()).decode()
        except Exception:
            gemini_key = None

    if not openai_key and not gemini_key:
        raise HTTPException(status_code=400, detail="no AI keys stored")

    try:
        text = await generate_text(openai_key=openai_key or "", gemini_key=gemini_key or "", prompt=payload.prompt, model=payload.model)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI providers failed: {e}")
    return {"result": text}


# ---- Social accounts ----
@app.get("/social/accounts")
async def social_accounts_list(jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    rows = await db.fetch_all("SELECT id, provider, provider_user_id, scopes, expires_at, created_at FROM social_accounts WHERE user_id = :uid", values={"uid": user_id})
    return {"accounts": [dict(r) for r in rows]}


@app.get("/social/accounts/{account_id}")
async def social_account_get(account_id: str, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    row = await db.fetch_one("SELECT id, provider, provider_user_id, scopes, expires_at, created_at FROM social_accounts WHERE id = :id AND user_id = :uid", values={"id": account_id, "uid": user_id})
    if not row:
        raise HTTPException(status_code=404, detail="not found")
    return dict(row)


@app.delete("/social/accounts/{account_id}")
async def social_account_delete(account_id: str, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    await db.execute("DELETE FROM social_accounts WHERE id = :id AND user_id = :uid", values={"id": account_id, "uid": user_id})
    return {"status": "deleted", "id": account_id}


# ---- Scheduling endpoints ----
@app.post("/schedule")
async def schedule_create(payload: ScheduleIn, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    if not payload.content:
        raise HTTPException(status_code=400, detail="content missing")
    # default immediate if scheduled_at missing
    scheduled_at = payload.scheduled_at or datetime.datetime.utcnow().isoformat()
    # insert
    row = await db.fetch_one(
        "INSERT INTO scheduled_posts (user_id, social_account_id, content, metadata, scheduled_at, status, created_at) VALUES (:u,:s,:c,:m,:st,'pending',NOW()) RETURNING id",
        values={"u": user_id, "s": payload.social_account_id, "c": payload.content, "m": payload.metadata or {}, "st": scheduled_at}
    )
    inserted_id = row[0] if row else None
    return {"status": "scheduled", "id": inserted_id}


@app.get("/schedule")
async def schedule_list(jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    rows = await db.fetch_all("SELECT id, social_account_id, content, metadata, scheduled_at, status, created_at FROM scheduled_posts WHERE user_id = :uid ORDER BY scheduled_at", values={"uid": user_id})
    return {"schedules": [dict(r) for r in rows]}


@app.delete("/schedule/{schedule_id}")
async def schedule_delete(schedule_id: str, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    await db.execute("DELETE FROM scheduled_posts WHERE id = :id AND user_id = :uid", values={"id": schedule_id, "uid": user_id})
    return {"status": "deleted", "id": schedule_id}


# ---- Publish now (instant publish) ----
@app.post("/posts/publish-now")
async def publish_now(payload: PublishNowIn, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    if not payload.social_account_id:
        raise HTTPException(status_code=400, detail="missing social_account_id")
    row = await db.fetch_one("SELECT * FROM social_accounts WHERE id = :id AND user_id = :uid", values={"id": payload.social_account_id, "uid": user_id})
    if not row:
        raise HTTPException(status_code=404, detail="social account not found")

    provider = row.get("provider")
    # Attempt to decrypt stored access_token/session if available
    access_blob = None
    if row.get("access_token"):
        try:
            access_blob = fernet.decrypt(row["access_token"].encode()).decode()
        except Exception:
            access_blob = None

    if provider == "instagram":
        if _publish_instagram_internal is None:
            raise HTTPException(status_code=500, detail="instagram publish helper not implemented on server")
        # call internal helper: account row, content, media list, access_blob (optional)
        result = await _publish_instagram_internal(row, payload.content, payload.media or [], access_token_blob=access_blob)
    elif provider == "youtube":
        if _publish_youtube_internal is None:
            raise HTTPException(status_code=500, detail="youtube upload helper not implemented on server")
        # expect first media url to be the video URL
        if not payload.media or len(payload.media) == 0:
            raise HTTPException(status_code=400, detail="youtube requires a video url in media")
        result = await _publish_youtube_internal(row, payload.media[0], payload.content)
    else:
        raise HTTPException(status_code=400, detail="provider not supported for instant publish")

    # record post in posts table
    await db.execute("INSERT INTO posts (user_id, platform, platform_post_id, content, metadata, created_at) VALUES (:u, :p, :pp, :c, :m, NOW())",
                     values={"u": user_id, "p": provider, "pp": result.get("platform_post_id"), "c": payload.content, "m": result.get("raw", {})})
    return {"status": "published", "result": result}


# ---- Posts history ----
@app.get("/posts/history")
async def posts_history(jwt_payload=Depends(verify_supabase_jwt), limit: int = 50):
    user_id = jwt_payload.get("sub")
    rows = await db.fetch_all("SELECT id, platform, platform_post_id, content, metadata, created_at FROM posts WHERE user_id = :uid ORDER BY created_at DESC LIMIT :lim", values={"uid": user_id, "lim": limit})
    return {"posts": [dict(r) for r in rows]}


@app.get("/posts/{platform}/{platform_post_id}")
async def posts_get(platform: str, platform_post_id: str, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    row = await db.fetch_one("SELECT * FROM posts WHERE user_id = :uid AND platform = :p AND platform_post_id = :pp LIMIT 1", values={"uid": user_id, "p": platform, "pp": platform_post_id})
    if not row:
        raise HTTPException(status_code=404, detail="post not found")
    return dict(row)


# ---- Analytics (on-demand overview) ----
@app.get("/analytics/overview")
async def analytics_overview(jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    result = {}
    rows = await db.fetch_all("SELECT id, provider, provider_user_id, access_token FROM social_accounts WHERE user_id = :uid", values={"uid": user_id})
    import httpx
    for r in rows:
        prov = r.get("provider")
        provider_user_id = r.get("provider_user_id")
        access_blob = None
        if r.get("access_token"):
            try:
                access_blob = fernet.decrypt(r["access_token"].encode()).decode()
            except Exception:
                access_blob = None
        try:
            if prov == "youtube" and access_blob:
                async with httpx.AsyncClient() as client:
                    resp = await client.get("https://www.googleapis.com/youtube/v3/channels", params={"part": "statistics,snippet", "id": provider_user_id, "access_token": access_blob})
                    if resp.status_code == 200:
                        result.setdefault("youtube", []).append(resp.json())
            elif prov == "instagram" and access_blob:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(f"https://graph.facebook.com/v18.0/{provider_user_id}", params={"fields": "username,followers_count,media_count", "access_token": access_blob})
                    if resp.status_code == 200:
                        result.setdefault("instagram", []).append(resp.json())
            else:
                result.setdefault("other", []).append(prov)
        except Exception as e:
            result.setdefault(f"{prov}_errors", []).append(str(e))
    return result


# ---- Analytics background worker + admin trigger ----
async def run_analytics_worker():
    rows = await db.fetch_all("SELECT id, user_id, provider, provider_user_id, access_token FROM social_accounts")
    import httpx
    for r in rows:
        prov = r.get("provider")
        user_id = r.get("user_id")
        access_blob = None
        if r.get("access_token"):
            try:
                access_blob = fernet.decrypt(r["access_token"].encode()).decode()
            except Exception:
                access_blob = None
        try:
            if prov == "youtube" and access_blob:
                async with httpx.AsyncClient() as client:
                    resp = await client.get("https://www.googleapis.com/youtube/v3/channels", params={"part": "statistics", "id": r.get("provider_user_id"), "access_token": access_blob})
                    if resp.status_code == 200:
                        await db.execute("INSERT INTO analytics_snapshots (user_id, provider, payload, created_at) VALUES (:u, :p, :pl, NOW())", values={"u": user_id, "p": "youtube", "pl": resp.text})
            elif prov == "instagram" and access_blob:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(f"https://graph.facebook.com/v18.0/{r.get('provider_user_id')}", params={"fields": "username,followers_count,media_count", "access_token": access_blob})
                    if resp.status_code == 200:
                        await db.execute("INSERT INTO analytics_snapshots (user_id, provider, payload, created_at) VALUES (:u, :p, :pl, NOW())", values={"u": user_id, "p": "instagram", "pl": resp.text})
        except Exception as e:
            print("analytics worker error", e)


@app.post("/admin/collect-analytics")
async def admin_collect_analytics(jwt_payload=Depends(verify_supabase_jwt), background_tasks: BackgroundTasks = None):
    # Consider restricting to admin role in production
    if background_tasks:
        background_tasks.add_task(asyncio.create_task, run_analytics_worker())
        return {"status": "started"}
    else:
        # synchronous fallback
        await run_analytics_worker()
        return {"status": "completed"}


# ---- Scheduled publisher (job) ----
async def run_scheduled_publisher():
    rows = await db.fetch_all("SELECT id, user_id, social_account_id, content, metadata FROM scheduled_posts WHERE status = 'pending' AND scheduled_at <= now() ORDER BY scheduled_at LIMIT 20")
    for r in rows:
        try:
            account_row = await db.fetch_one("SELECT * FROM social_accounts WHERE id = :id", values={"id": r.get("social_account_id")})
            if not account_row:
                await db.execute("UPDATE scheduled_posts SET status='failed' WHERE id = :id", values={"id": r.get("id")})
                continue

            prov = account_row.get("provider")
            metadata = r.get("metadata") or {}
            # Decrypt session/access token if present
            access_blob = None
            if account_row.get("access_token"):
                try:
                    access_blob = fernet.decrypt(account_row["access_token"].encode()).decode()
                except Exception:
                    access_blob = None

            if prov == "instagram":
                if _publish_instagram_internal is None:
                    raise RuntimeError("instagram publish helper missing")
                media_url = metadata.get("media_url")
                media_list = [media_url] if media_url else []
                res = await _publish_instagram_internal(account_row, r.get("content"), media_list, access_token_blob=access_blob)
            elif prov == "youtube":
                if _publish_youtube_internal is None:
                    raise RuntimeError("youtube upload helper missing")
                media_url = metadata.get("media_url")
                res = await _publish_youtube_internal(account_row, media_url, r.get("content"))
            else:
                # unsupported provider
                await db.execute("UPDATE scheduled_posts SET status='failed' WHERE id = :id", values={"id": r.get("id")})
                continue

            # record post & update scheduled_posts
            await db.execute("INSERT INTO posts (user_id, platform, platform_post_id, content, metadata, created_at) VALUES (:u, :p, :pp, :c, :m, NOW())", values={"u": r.get("user_id"), "p": prov, "pp": res.get("platform_post_id"), "c": r.get("content"), "m": res.get("raw", {})})
            await db.execute("UPDATE scheduled_posts SET status = 'published', provider_post_id = :pp WHERE id = :id", values={"pp": res.get("platform_post_id"), "id": r.get("id")})
        except Exception as e:
            print("scheduled publish error", e)
            try:
                await db.execute("UPDATE scheduled_posts SET status='failed' WHERE id = :id", values={"id": r.get("id")})
            except Exception:
                pass



