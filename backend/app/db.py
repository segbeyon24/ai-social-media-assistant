"""
Database helpers using databases + SQLAlchemy engine.
Adjust DATABASE_URL in env (from Supabase) before running.
"""
import os
from databases import Database
from sqlalchemy import create_engine, MetaData

DATABASE_URL = os.getenv("DATABASE_URL")

# Render Postgres session mode supports very few concurrent DB connections.
database = Database(
    DATABASE_URL,
    min_size=1,
    max_size=2  # NEVER exceed 2 on Render free/basic Postgres.
)

engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Utility convenience wrappers could be added here
