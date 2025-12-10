"""
Database helpers using databases + SQLAlchemy engine.
Adjust DATABASE_URL in env (from Supabase) before running.
"""
import os
from databases import Database
from sqlalchemy import create_engine, MetaData

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    # In Supabase, use the full postgres connection string (service_role key recommended for server)
    raise RuntimeError('DATABASE_URL env var must be set to your Supabase Postgres URL')

db = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Utility convenience wrappers could be added here
