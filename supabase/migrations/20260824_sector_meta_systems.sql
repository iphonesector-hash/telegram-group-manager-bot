CREATE TABLE IF NOT EXISTS isectorbot_sector_world_bosses (
  id BIGSERIAL PRIMARY KEY,
  season_key TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  hp BIGINT NOT NULL CHECK (hp >= 0),
  max_hp BIGINT NOT NULL CHECK (max_hp > 0),
  reward_pool BIGINT NOT NULL DEFAULT 0 CHECK (reward_pool >= 0),
  active BOOLEAN NOT NULL DEFAULT TRUE,
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  ends_at TIMESTAMPTZ NOT NULL,
  defeated_at TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS isectorbot_sector_boss_hits (
  id BIGSERIAL PRIMARY KEY,
  boss_id BIGINT NOT NULL REFERENCES isectorbot_sector_world_bosses(id) ON DELETE CASCADE,
  user_id BIGINT NOT NULL REFERENCES isectorbot_users(id) ON DELETE CASCADE,
  damage BIGINT NOT NULL DEFAULT 0 CHECK (damage >= 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_sector_boss_hit_user_created ON isectorbot_sector_boss_hits(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS ix_sector_boss_hit_boss_damage ON isectorbot_sector_boss_hits(boss_id, damage DESC);

CREATE TABLE IF NOT EXISTS isectorbot_sector_reward_claims (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES isectorbot_users(id) ON DELETE CASCADE,
  claim_key TEXT NOT NULL,
  period_key TEXT NOT NULL,
  reward JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_sector_reward_claim UNIQUE(user_id, claim_key, period_key)
);
CREATE INDEX IF NOT EXISTS ix_sector_reward_claim_user_created ON isectorbot_sector_reward_claims(user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS isectorbot_sector_ledger (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES isectorbot_users(id) ON DELETE CASCADE,
  kind TEXT NOT NULL,
  amount BIGINT NOT NULL DEFAULT 0,
  balance_after BIGINT NOT NULL DEFAULT 0,
  ref_type TEXT,
  ref_key TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_sector_ledger_user_created ON isectorbot_sector_ledger(user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS isectorbot_sector_analytics (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES isectorbot_users(id) ON DELETE CASCADE,
  event TEXT NOT NULL,
  context TEXT NOT NULL DEFAULT 'miniapp',
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_sector_analytics_event_created ON isectorbot_sector_analytics(event, created_at DESC);
CREATE INDEX IF NOT EXISTS ix_sector_analytics_user_created ON isectorbot_sector_analytics(user_id, created_at DESC);
