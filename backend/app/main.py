"""
Complete main.py for AI Social Manager v0.4

- Integrates YouTube + Instagram routers (attempts multiple import paths)
- Exposes unified endpoints expected by the frontend:
  - /health
  - /user/ai-key  (POST, GET, DELETE)
  - /ai/generate
  - /social/accounts (list, get, delete)
  - /auth/<platform> routers (youtube/instagram included)
  - /schedule (create, list, delete)
  - /posts/publish-now
  - /posts/history
  - /analytics/overview (on-demand)
- Lightweight cron worker function `collect_analytics_worker()` to be run as Render background job.
"""

import os
import asyncio
import time
import datetime
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from cryptography.fernet import Fernet

# core app modules (these must exist in your repo)
from .auth_supabase import verify_supabase_jwt
from .db import db
from .ai_adapter import generate_text

# Try flexible imports for youtube / instagram routers (some repos vary in folder names)
def _try_import(module_path: str, attr: str = "router"):
    try:
        mod = __import__(module_path, fromlist=[attr])
        return getattr(mod, attr)
    except Exception:
        return None

# YouTube routers (auth, upload, api)
youtube_auth_router = _try_import(".youtube.auth_youtube", "router") or _try_import(".youtub.auth_youtube", "router")
youtube_upload_router = _try_import(".youtube.youtube_upload", "router") or _try_import(".youtub.youtube_upload", "router")
youtube_api_router = _try_import(".youtube.youtube_api", "router") or _try_import(".youtub.youtube_api", "router")

# Instagram routers
instagram_auth_router = _try_import(".instagram.auth_instagram", "router") or _try_import(".insta.auth_instagram", "router")
instagram_api_router = _try_import(".instagram.instagram_api", "router") or _try_import(".insta.instagram_api", "router")

# If routers could not be imported that will be None — safe to include conditionally later.

app = FastAPI(title="AI Social Manager - Backend v0.4")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fernet encryption
FERNET_KEY = os.getenv("FERNET_KEY")
if not FERNET_KEY:
    raise RuntimeError("FERNET_KEY must be set in environment")
fernet = Fernet(FERNET_KEY.encode())

# --- Pydantic models ---
class StoreAIKeyIn(BaseModel):
    provider: str
    api_key: str

class GenerateIn(BaseModel):
    prompt: str
    model: Optional[str] = "gpt-4o-mini"

class ScheduleIn(BaseModel):
    social_account_id: str
    content: str
    scheduled_at: Optional[str] = None  # ISO string

class PublishNowIn(BaseModel):
    social_account_id: str
    content: str
    media: Optional[List[str]] = None  # list of image/video URLs

# ---------------------------
# Lifecycle events
# ---------------------------
@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

# ---------------------------
# Health
# ---------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "time": int(time.time())}

# ---------------------------
# AI Key endpoints (store/get/delete)
# ---------------------------
@app.post("/user/ai-key")
async def store_ai_key(payload: StoreAIKeyIn, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    if not user_id:
        raise HTTPException(401, "unauthenticated")
    if payload.provider.lower() not in ("openai", "gemini"):
        raise HTTPException(400, "provider must be 'openai' or 'gemini'")

    encrypted = fernet.encrypt(payload.api_key.encode()).decode()
    query = """
        INSERT INTO user_api_keys (user_id, provider, encrypted_api_key, created_at)
        VALUES (:uid, :prov, :enc, NOW())
        ON CONFLICT (user_id, provider) DO UPDATE SET encrypted_api_key = EXCLUDED.encrypted_api_key, created_at = NOW()
    """
    await db.execute(query=query, values={"uid": user_id, "prov": payload.provider.lower(), "enc": encrypted})
    return {"status": "ok", "provider": payload.provider.lower()}

@app.get("/user/ai-key")
async def get_ai_keys(jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    rows = await db.fetch_all("SELECT provider, created_at FROM user_api_keys WHERE user_id = :uid", values={"uid": user_id})
    return {"keys": [dict(r) for r in rows]}

@app.delete("/user/ai-key/{provider}")
async def delete_ai_key(provider: str, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    await db.execute("DELETE FROM user_api_keys WHERE user_id = :uid AND provider = :prov", values={"uid": user_id, "prov": provider})
    return {"status": "deleted", "provider": provider}

# ---------------------------
# Helper: fetch & decrypt user AI key
# ---------------------------
async def _get_decrypted_api_key(user_id: str, provider: str) -> Optional[str]:
    row = await db.fetch_one("SELECT encrypted_api_key FROM user_api_keys WHERE user_id = :uid AND provider = :prov", values={"uid": user_id, "prov": provider})
    if not row:
        return None
    enc = row["encrypted_api_key"]
    try:
        return fernet.decrypt(enc.encode()).decode()
    except Exception:
        return None

# ---------------------------
# AI Generate endpoint (failover)
# ---------------------------
@app.post("/ai/generate")
async def ai_generate(payload: GenerateIn, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    openai_key = await _get_decrypted_api_key(user_id, "openai")
    gemini_key = await _get_decrypted_api_key(user_id, "gemini")
    if not openai_key and not gemini_key:
        raise HTTPException(400, "no AI keys stored")

    try:
        text = await generate_text(openai_key=openai_key or "", gemini_key=gemini_key or "", prompt=payload.prompt, model=payload.model)
    except Exception as e:
        raise HTTPException(502, f"AI providers failed: {e}")
    return {"result": text}

# ---------------------------
# Social accounts endpoints (list/get/delete)
# ---------------------------
@app.get("/social/accounts")
async def list_social_accounts(jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    rows = await db.fetch_all("SELECT id, provider, provider_user_id, scopes, expires_at, created_at FROM social_accounts WHERE user_id = :uid", values={"uid": user_id})
    result = []
    for r in rows:
        rec = dict(r)
        # mask tokens (do not return tokens)
        rec.pop("access_token", None)
        rec.pop("refresh_token", None)
        result.append(rec)
    return {"accounts": result}

@app.get("/social/accounts/{account_id}")
async def get_social_account(account_id: str, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    row = await db.fetch_one("SELECT id, provider, provider_user_id, scopes, expires_at, created_at FROM social_accounts WHERE id = :id AND user_id = :uid", values={"id": account_id, "uid": user_id})
    if not row:
        raise HTTPException(404, "not found")
    return dict(row)

@app.delete("/social/accounts/{account_id}")
async def delete_social_account(account_id: str, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    await db.execute("DELETE FROM social_accounts WHERE id = :id AND user_id = :uid", values={"id": account_id, "uid": user_id})
    return {"status": "deleted", "id": account_id}

# ---------------------------
# Schedule endpoints (create/list/delete)
# ---------------------------
@app.post("/schedule")
async def create_schedule(payload: ScheduleIn, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    if not payload.content:
        raise HTTPException(400, "content missing")
    scheduled_at = payload.scheduled_at or datetime.datetime.utcnow().isoformat()
    query = """
        INSERT INTO scheduled_posts (user_id, social_account_id, content, scheduled_at, created_at)
        VALUES (:uid, :sid, :content, :sched, NOW())
        RETURNING id
    """
    row_id = await db.fetch_one(query=query, values={"uid": user_id, "sid": payload.social_account_id, "content": payload.content, "sched": scheduled_at})
    return {"status": "scheduled", "id": row_id[0] if row_id else None}

@app.get("/schedule")
async def list_schedules(jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    rows = await db.fetch_all("SELECT id, social_account_id, content, scheduled_at, created_at FROM scheduled_posts WHERE user_id = :uid ORDER BY scheduled_at", values={"uid": user_id})
    return {"schedules": [dict(r) for r in rows]}

@app.delete("/schedule/{schedule_id}")
async def delete_schedule(schedule_id: str, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    await db.execute("DELETE FROM scheduled_posts WHERE id = :id AND user_id = :uid", values={"id": schedule_id, "uid": user_id})
    return {"status": "deleted", "id": schedule_id}

# ---------------------------
# Publish now endpoint (instant publish)
# ---------------------------
@app.post("/posts/publish-now")
async def publish_now(payload: PublishNowIn, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    # find social account
    row = await db.fetch_one("SELECT * FROM social_accounts WHERE id = :id AND user_id = :uid", values={"id": payload.social_account_id, "uid": user_id})
    if not row:
        raise HTTPException(404, "social account not connected")

    provider = row["provider"]
    # decrypt tokens if needed
    access_token = None
    if row.get("access_token"):
        try:
            access_token = fernet.decrypt(row["access_token"].encode()).decode()
        except Exception:
            access_token = None

    # Minimal unified publish logic — call provider-specific routers internally via httpx to route or call helper functions
    # We'll implement two paths inline: instagram & youtube; other providers should have their own helper modules.
    if provider == "instagram":
        # call instagram publish endpoint defined in instagram_api (if exists)
        # prefer internal function if instagram_api exposes publish route
        publish_result = await _publish_instagram_now(row, payload.content, payload.media, access_token)
    elif provider == "youtube":
        publish_result = await _publish_youtube_now(row, payload.content, payload.media, access_token)
    else:
        raise HTTPException(400, "provider not supported for instant publish")

    # store post record
    await db.execute("INSERT INTO posts (user_id, platform, platform_post_id, content, created_at) VALUES (:u, :p, :pp, :c, NOW())", values={"u": user_id, "p": provider, "pp": publish_result.get("platform_post_id"), "c": payload.content})
    return {"status": "published", "result": publish_result}

# Provider-specific helpers (simplified: adapt to your provider modules)
async def _publish_instagram_now(account_row, content: str, media: Optional[List[str]], access_token: Optional[str]):
    # Instagram Graph API: create media container -> publish
    if not access_token:
        # attempt to decrypt from stored access_token column (some flows store encrypted tokens in social_accounts)
        if account_row.get("access_token"):
            try:
                access_token = fernet.decrypt(account_row["access_token"].encode()).decode()
            except:
                access_token = None
    if not access_token:
        raise HTTPException(401, "instagram token missing")

    ig_id = account_row.get("provider_user_id")
    if not ig_id:
        raise HTTPException(400, "instagram business account id not found")

    import httpx
    async with httpx.AsyncClient() as client:
        # for simplicity support single-image posts
        if not media or len(media) == 0:
            raise HTTPException(400, "instagram requires image/video media_url for publishing via API")
        image_url = media[0]
        create_res = await client.post(f"https://graph.facebook.com/v18.0/{ig_id}/media", params={"image_url": image_url, "caption": content, "access_token": access_token})
        create_res.raise_for_status()
        creation = create_res.json()
        creation_id = creation.get("id")
        if not creation_id:
            raise HTTPException(500, f"instagram media creation failed: {creation}")
        publish_res = await client.post(f"https://graph.facebook.com/v18.0/{ig_id}/media_publish", params={"creation_id": creation_id, "access_token": access_token})
        publish_res.raise_for_status()
        published = publish_res.json()
        return {"platform_post_id": published.get("id"), "raw": published}

async def _publish_youtube_now(account_row, content: str, media: Optional[List[str]], access_token: Optional[str]):
    # YouTube upload: expect media[0] to be a publicly accessible video URL
    if not access_token:
        if account_row.get("access_token"):
            try:
                access_token = fernet.decrypt(account_row["access_token"].encode()).decode()
            except:
                access_token = None
    if not access_token:
        raise HTTPException(401, "youtube token missing")
    if not media or len(media) == 0:
        raise HTTPException(400, "youtube requires video url to upload")
    video_url = media[0]
    import httpx, tempfile, os
    # download the video then perform resumable upload to YouTube using the same flow your youtube_upload router uses
    async with httpx.AsyncClient() as client:
        r = await client.get(video_url, timeout=120)
        r.raise_for_status()
        # write to temp file
        tmp = tempfile.mktemp(suffix=".mp4")
        with open(tmp, "wb") as f:
            f.write(r.content)
        # initiate resumable upload
        metadata = {"snippet": {"title": content[:80], "description": content}, "status": {"privacyStatus": "public"}}
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json; charset=UTF-8"}
        init = await client.post("https://www.googleapis.com/upload/youtube/v3/videos?part=snippet,status&uploadType=resumable", json=metadata, headers=headers)
        init.raise_for_status()
        upload_url = init.headers.get("Location")
        if not upload_url:
            raise HTTPException(500, "youtube did not return upload URL")
        # upload file bytes
        file_size = os.path.getsize(tmp)
        with open(tmp, "rb") as fh:
            put = await client.put(upload_url, content=fh.read(), headers={"Content-Length": str(file_size), "Content-Type": "video/*", "Authorization": f"Bearer {access_token}"}, timeout=600)
            put.raise_for_status()
            resp = put.json()
        try:
            os.remove(tmp)
        except Exception:
            pass
        return {"platform_post_id": resp.get("id"), "raw": resp}

# ---------------------------
# Posts history endpoints
# ---------------------------
@app.get("/posts/history")
async def posts_history(jwt_payload=Depends(verify_supabase_jwt), limit: int = 50):
    user_id = jwt_payload.get("sub")
    rows = await db.fetch_all("SELECT id, platform, platform_post_id, content, created_at FROM posts WHERE user_id = :uid ORDER BY created_at DESC LIMIT :lim", values={"uid": user_id, "lim": limit})
    return {"posts": [dict(r) for r in rows]}

@app.get("/posts/{platform}/{platform_post_id}")
async def get_post(platform: str, platform_post_id: str, jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    row = await db.fetch_one("SELECT * FROM posts WHERE user_id = :uid AND platform = :p AND platform_post_id = :pp LIMIT 1", values={"uid": user_id, "p": platform, "pp": platform_post_id})
    if not row:
        raise HTTPException(404, "post not found")
    return dict(row)

# ---------------------------
# Analytics endpoints (on-demand)
# ---------------------------
@app.get("/analytics/overview")
async def analytics_overview(jwt_payload=Depends(verify_supabase_jwt)):
    user_id = jwt_payload.get("sub")
    # gather basic per-platform metrics (call provider-specific routers/helpers)
    result = {}
    rows = await db.fetch_all("SELECT id, provider, provider_user_id, expires_at FROM social_accounts WHERE user_id = :uid", values={"uid": user_id})
    for r in rows:
        prov = r["provider"]
        if prov == "youtube":
            # call youtube_api endpoint (internal)
            # best to import and call its helper if available; fallback to simple API call
            try:
                # attempt to call youtube api router helper using httpx to our own server (internal)
                # but here we'll do a direct minimal request using stored token
                access = None
                if r.get("access_token"): access = fernet.decrypt(r["access_token"].encode()).decode()
                if access:
                    import httpx
                    # fetch channel stats
                    chan_id = r.get("provider_user_id")
                    async with httpx.AsyncClient() as client:
                        resp = await client.get("https://www.googleapis.com/youtube/v3/channels", params={"part":"statistics", "id": chan_id, "access_token": access})
                        if resp.status_code == 200:
                            data = resp.json()
                            result.setdefault("youtube", []).append(data)
            except Exception as e:
                result.setdefault("youtube_errors", []).append(str(e))
        elif prov == "instagram":
            try:
                access = None
                if r.get("access_token"): access = fernet.decrypt(r["access_token"].encode()).decode()
                if access:
                    import httpx
                    ig_id = r.get("provider_user_id")
                    async with httpx.AsyncClient() as client:
                        resp = await client.get(f"https://graph.facebook.com/v18.0/{ig_id}", params={"fields":"username,followers_count,media_count", "access_token": access})
                        if resp.status_code == 200:
                            data = resp.json()
                            result.setdefault("instagram", []).append(data)
            except Exception as e:
                result.setdefault("instagram_errors", []).append(str(e))
        else:
            result.setdefault("other", []).append(prov)
    return result

# ---------------------------
# Background worker: analytics collection
# ---------------------------
async def collect_analytics_worker():
    """
    This function can be run as a separate process (Render background worker)
    or invoked via a scheduler. It will iterate connected social_accounts and
    fetch metrics, writing them into analytics snapshots tables.

    Usage: run `python -c "import asyncio; from app.main import collect_analytics_worker; asyncio.run(collect_analytics_worker())"`
    or configure a Render cron to call an endpoint that triggers it (small wrapper below).
    """
    rows = await db.fetch_all("SELECT id, user_id, provider, provider_user_id, access_token, refresh_token FROM social_accounts")
    import httpx
    for r in rows:
        provider = r["provider"]
        user_id = r["user_id"]
        try:
            if provider == "youtube":
                access = None
                if r.get("access_token"):
                    try:
                        access = fernet.decrypt(r["access_token"].encode()).decode()
                    except:
                        access = None
                if not access and r.get("refresh_token"):
                    # try refresh flow if available - here we skip (implement refresh helper in youtube module)
                    pass
                if access:
                    chan_id = r.get("provider_user_id")
                    async with httpx.AsyncClient() as client:
                        resp = await client.get("https://www.googleapis.com/youtube/v3/channels", params={"part":"statistics", "id": chan_id, "access_token": access})
                        if resp.status_code == 200:
                            data = resp.json()
                            # persist minimal snapshot
                            await db.execute("INSERT INTO analytics_snapshots (user_id, provider, payload, created_at) VALUES (:u, :p, :pl, NOW())", values={"u": user_id, "p": "youtube", "pl": str(data)})
            elif provider == "instagram":
                access = None
                if r.get("access_token"):
                    try:
                        access = fernet.decrypt(r["access_token"].encode()).decode()
                    except:
                        access = None
                if access:
                    ig_id = r.get("provider_user_id")
                    async with httpx.AsyncClient() as client:
                        resp = await client.get(f"https://graph.facebook.com/v18.0/{ig_id}", params={"fields":"followers_count,media_count,username", "access_token": access})
                        if resp.status_code == 200:
                            data = resp.json()
                            await db.execute("INSERT INTO analytics_snapshots (user_id, provider, payload, created_at) VALUES (:u, :p, :pl, NOW())", values={"u": user_id, "p": "instagram", "pl": str(data)})
            else:
                continue
        except Exception as e:
            # log and continue
            print("analytics worker error for row", r.get("id"), str(e))

# optional endpoint to trigger worker manually (for testing)
@app.post("/admin/collect-analytics")
async def trigger_collect_analytics(jwt_payload=Depends(verify_supabase_jwt), background_tasks: BackgroundTasks = None):
    # NOTE: you may want to restrict this endpoint to admins only
    background_tasks.add_task(asyncio.create_task, collect_analytics_worker())
    return {"status": "ok", "started": True}

# ---------------------------
# Include third-party routers if available
# ---------------------------
if youtube_auth_router:
    app.include_router(youtube_auth_router, prefix="/auth/youtube", tags=["YouTube OAuth"])
if youtube_upload_router:
    app.include_router(youtube_upload_router, prefix="/youtube", tags=["YouTube Upload"])
if youtube_api_router:
    app.include_router(youtube_api_router, prefix="/youtube", tags=["YouTube API"])

if instagram_auth_router:
    app.include_router(instagram_auth_router, prefix="/auth/instagram", tags=["Instagram OAuth"])
if instagram_api_router:
    app.include_router(instagram_api_router, prefix="/instagram", tags=["Instagram API"])

# ---------------------------
# Done
# ---------------------------
