
Backend Summary

3.1 Backend Stack

    Language: Python 3.13
    Framework: FastAPI
    Database: Supabase Postgres
    Auth: Supabase JWT + OAuth
    Async DB: databases + asyncpg
    Deployment: Render
    Task readiness: Celery / APScheduler (planned)

3.2 Backend Directory Structure

backend/
├── Dockerfile
├── README.md
├── requirements.txt
└── app/
    ├── main.py
    ├── db.py
    ├── models.py
    ├── auth_supabase.py
    ├── auth_local.py
    ├── ai_adapter.py
    ├── tasks.py
    │
    ├── instagram/
    │   ├── auth_instagram.py
    │   └── instagram_api.py
    │
    ├── youtube/
    │   ├── auth_youtube.py
    │   ├── youtube_api.py
    │   ├── youtube_upload.py
    │   └── table.sql
    │
    ├── migrations/
    │   └── sql_migrations_v1.sql
    │
    ├── scripts/
    │   └── run_migrations.py
    │
    └── utils/
        └── crypto.py



3.3 Backend Responsibilities

Authentication
    Supabase JWT verification
    OAuth token exchange and refresh
    Provider-specific token storage
    Secure encryption at rest

Social Platform Integration
    YouTube:
        OAuth
        Video upload
        Engagement analytics

    Instagram:
        OAuth
        Media insights
        User engagement metrics

Analytics
    User-centric and post-centric metrics
    Engagement normalization across platforms
    Ready for AI summarization

AI Adapter
    Central abstraction for:
        Caption generation
        Post optimization
        Analytics insights

    Model-agnostic (OpenAI, local, future fine-tuned models)

Stability
    Explicit startup/shutdown lifecycle
    Graceful DB connection handling
    Environment-driven configuration



3.4 Known Backend Limitations

| Area            | Limitation                          |
| --------------- | ----------------------------------- |
| DB Connections  | Supabase session mode client limits |
| Tasks           | Background jobs not yet active      |
| Error Isolation | Some platform errors can cascade    |
| Rate Limits     | Platform APIs not yet throttled     |
| Observability   | No tracing/log aggregation          |


3.5 Backend Upgrade Paths
    Introduce connection pooling strategy
    Enable Celery / APScheduler
    Add Redis for caching + rate limits
    Per-platform circuit breakers
    Observability (OpenTelemetry)
    Platform abstraction layer (TikTok, X)