-- Basic bootstrap for dev Postgres. Runs once at container init.
-- Safe to keep idempotent statements only.

CREATE SCHEMA IF NOT EXISTS app;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Placeholder table for notes/history (applications can replace with migrations).
CREATE TABLE IF NOT EXISTS app.chat_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON SCHEMA app IS 'Application objects live here; replace with migrations for prod.';
COMMENT ON TABLE app.chat_notes IS 'Lightweight placeholder table; swap for real models.';
