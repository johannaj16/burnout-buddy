-- Initial schema for backend evening snapshot persistence.

CREATE TABLE IF NOT EXISTS evenings (
  id BIGSERIAL PRIMARY KEY,
  evening_id VARCHAR(128) NOT NULL,
  user_id VARCHAR(128) NOT NULL,
  state VARCHAR(64) NOT NULL,
  rest_extended_once BOOLEAN NOT NULL DEFAULT FALSE,
  plan_locked BOOLEAN NOT NULL DEFAULT FALSE,
  rest_active BOOLEAN NOT NULL DEFAULT FALSE,
  scroll_block_active BOOLEAN NOT NULL DEFAULT FALSE,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_evening_user UNIQUE (evening_id, user_id)
);
