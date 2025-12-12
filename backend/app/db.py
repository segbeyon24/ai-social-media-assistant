"""
Database helpers using databases + SQLAlchemy engine.
Adjust DATABASE_URL in env (from Supabase) before running.
"""
import os
from databases import Database
from sqlalchemy import create_engine, MetaData

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Render Postgres session mode supports very few concurrent DB connections.
db = Database(
    DATABASE_URL,
    min_size=1,
    max_size=2  
)

engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Utility convenience wrappers could be added here
