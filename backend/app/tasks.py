# app/tasks.py
"""
APScheduler task definitions and helpers for scheduled posts and analytics.
This module centralizes the scheduling logic used by main.py.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
from app.db import db
from app.utils.crypto import decrypt

scheduler = AsyncIOScheduler()

async def publish_due_posts():
    rows = await db.fetch_all("SELECT id, user_id, social_account_id, content, metadata FROM scheduled_posts WHERE status='pending' AND scheduled_at <= now() ORDER BY scheduled_at LIMIT 20")
    for r in rows:
        try:
            account = await db.fetch_one("SELECT * FROM social_accounts WHERE id = :id", values={"id": r['social_account_id']})
            if not account:
                await db.execute("UPDATE scheduled_posts SET status='failed' WHERE id = :id", values={"id": r['id']})
                continue
            provider = account['provider']
            if provider == 'instagram':
                # call instagram internal helper
                from app.instagram.instagram_api import publish_now_internal
                media = (r.get('metadata') or {}).get('media_url')
                res = await publish_now_internal(account, r['content'], [media] if media else None)
            elif provider == 'youtube':
                from app.youtube.youtube_upload import upload_from_url_internal
                media = (r.get('metadata') or {}).get('media_url')
                res = await upload_from_url_internal(account, media, r['content'])
            else:
                res = {'error': 'unsupported'}
            await db.execute("INSERT INTO posts (user_id, platform, platform_post_id, content, created_at) VALUES (:u,:p,:pp,:c,NOW())", values={"u": r['user_id'], "p": provider, "pp": res.get('platform_post_id'), "c": r['content']})
            await db.execute("UPDATE scheduled_posts SET status='published', provider_post_id = :pp WHERE id = :id", values={"pp": res.get('platform_post_id'), "id": r['id']})
        except Exception as e:
            print('publish_due_posts error', e)
            await db.execute("UPDATE scheduled_posts SET status='failed' WHERE id = :id", values={"id": r['id']})

def start_scheduler():
    scheduler.add_job(publish_due_posts, trigger=IntervalTrigger(seconds=60), id='publish_due_posts', replace_existing=True)
    scheduler.start()
