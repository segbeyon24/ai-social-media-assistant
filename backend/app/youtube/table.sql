-- Ensure social_accounts exists (if you used earlier oauth_sql.sql it should already exist)
CREATE TABLE IF NOT EXISTS social_accounts (
id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
provider text NOT NULL,
provider_user_id text,
access_token text,
refresh_token text,
scopes text[],
expires_at timestamptz,
created_at timestamptz DEFAULT now(),
UNIQUE (user_id, provider)
);


-- Index for lookups
CREATE INDEX IF NOT EXISTS idx_social_accounts_user_provider ON social_accounts(user_id, provider);