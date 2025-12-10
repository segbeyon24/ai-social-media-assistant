# scripts/run_migrations.py
"""
Utility script to run SQL migrations against your DATABASE_URL.
Usage (locally):
  python scripts/run_migrations.py

It expects env var DATABASE_URL to be set (Supabase connection string) and will execute the sql file migrations/sql_migrations_v1.sql

Note: This script uses psycopg (psycopg2). If not installed, run `pip install psycopg[binary]` or adapt to use asyncpg.
"""
import os
import sys

SQL_PATH = os.path.join(os.path.dirname(__file__), '..', 'migrations', 'sql_migrations_v1.sql')
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print('DATABASE_URL environment variable must be set')
    sys.exit(1)

try:
    import psycopg
except Exception:
    print('psycopg not installed. Install with: pip install psycopg[binary]')
    sys.exit(1)

with open(SQL_PATH, 'r') as fh:
    sql = fh.read()

print('Running migrations...')

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()

print('Migrations executed successfully')
