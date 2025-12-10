-- SQL migrations for AI Social Manager v0.4
-- Run these in Supabase SQL editor (or via psql) to create missing tables

-- 1) scheduled_posts: stores posts the user scheduled to publish
CREATE TABLE IF NOT EXISTS scheduled_posts (
id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
social_account_id uuid NOT NULL,
content text NOT NULL,
metadata jsonb DEFAULT '{}'::jsonb,
scheduled_at timestamptz NOT NULL,
status varchar(32) DEFAULT 'pending', -- pending | published | failed | cancelled
provider_post_id text,
created_at timestamptz DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_user ON scheduled_posts(user_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_status ON scheduled_posts(status);

-- 2) posts: a record of published or attempted posts
CREATE TABLE IF NOT EXISTS posts (
id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
platform text NOT NULL,
platform_post_id text,
content text,
metadata jsonb DEFAULT '{}'::jsonb,
created_at timestamptz DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_posts_user ON posts(user_id);
CREATE INDEX IF NOT EXISTS idx_posts_platform ON posts(platform);

-- 3) analytics_snapshots: store periodic snapshots of metrics
CREATE TABLE IF NOT EXISTS analytics_snapshots (
id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
provider text NOT NULL,
payload jsonb NOT NULL,
created_at timestamptz DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_analytics_user ON analytics_snapshots(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_provider ON analytics_snapshots(provider);

-- 4) Ensure social_accounts has token columns (safe alter if missing)
ALTER TABLE social_accounts
ADD COLUMN IF NOT EXISTS access_token text,
ADD COLUMN IF NOT EXISTS refresh_token text,
ADD COLUMN IF NOT EXISTS provider_user_id text;

-- 5) Ensure user_api_keys has created_at
ALTER TABLE user_api_keys
ADD COLUMN IF NOT EXISTS created_at timestamptz DEFAULT now();

-- 6) Optional housekeeping: a table for oauth_states already exists in your schema.

-- End of migrations
