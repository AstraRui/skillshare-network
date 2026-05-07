-- SkillShare Network DB schema according to the provided ERD screenshot.
-- This script is safe to run on first docker init.

CREATE EXTENSION IF NOT EXISTS citext;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'skillshare_app') THEN
        CREATE ROLE skillshare_app LOGIN PASSWORD 'skillshare_app_password' NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
    END IF;
END $$;

CREATE TYPE user_role_enum AS ENUM ('user', 'admin');

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email CITEXT UNIQUE NOT NULL,
    phone VARCHAR(20),
    password_hash TEXT NOT NULL,
    full_name VARCHAR,
    avatar_url TEXT,
    rating NUMERIC(3,2) NOT NULL DEFAULT 0 CHECK (rating >= 0 AND rating <= 5),
    role user_role_enum NOT NULL DEFAULT 'user',
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS skill_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    parent_id INT REFERENCES skill_categories(id) ON DELETE SET NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    is_moderated BOOLEAN NOT NULL DEFAULT FALSE,
    moderated_by BIGINT REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    category_id INT NOT NULL REFERENCES skill_categories(id) ON DELETE RESTRICT,
    description TEXT,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    is_moderated BOOLEAN NOT NULL DEFAULT FALSE,
    moderated_by BIGINT REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS user_skills_offered (
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_id INT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    level SMALLINT NOT NULL CHECK (level BETWEEN 1 AND 5),
    description TEXT,
    PRIMARY KEY (user_id, skill_id)
);

CREATE TABLE IF NOT EXISTS user_skills_wanted (
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_id INT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    desired_level SMALLINT NOT NULL CHECK (desired_level BETWEEN 1 AND 5),
    priority SMALLINT NOT NULL DEFAULT 1 CHECK (priority BETWEEN 1 AND 3),
    PRIMARY KEY (user_id, skill_id)
);

CREATE TABLE IF NOT EXISTS exchanges (
    id BIGSERIAL PRIMARY KEY,
    initiator_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    status VARCHAR NOT NULL DEFAULT 'created',
    is_chain BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    is_moderated BOOLEAN NOT NULL DEFAULT FALSE,
    moderated_by BIGINT REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS exchange_participants (
    exchange_id BIGINT NOT NULL REFERENCES exchanges(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    gives_skill_id INT NOT NULL REFERENCES skills(id) ON DELETE RESTRICT,
    gets_skill_id INT NOT NULL REFERENCES skills(id) ON DELETE RESTRICT,
    position SMALLINT NOT NULL DEFAULT 1,
    PRIMARY KEY (exchange_id, user_id),
    UNIQUE (exchange_id, position)
);

CREATE TABLE IF NOT EXISTS reviews (
    id BIGSERIAL PRIMARY KEY,
    exchange_id BIGINT NOT NULL REFERENCES exchanges(id) ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    reviewed_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    rating SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    is_moderated BOOLEAN NOT NULL DEFAULT FALSE,
    is_hidden BOOLEAN NOT NULL DEFAULT FALSE,
    moderated_by BIGINT REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id BIGSERIAL PRIMARY KEY,
    exchange_id BIGINT NOT NULL REFERENCES exchanges(id) ON DELETE CASCADE,
    assignee_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    title VARCHAR NOT NULL,
    status VARCHAR NOT NULL DEFAULT 'todo'
);

CREATE TABLE IF NOT EXISTS messages (
    id BIGSERIAL PRIMARY KEY,
    task_id BIGINT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    sender_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    content TEXT,
    media_url TEXT,
    media_type TEXT CHECK (media_type IS NULL OR media_type IN ('photo','video','audio')),
    media_size INTEGER CHECK (media_size IS NULL OR media_size >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- Indexes for FK and matching queries
CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
CREATE INDEX IF NOT EXISTS ix_users_active ON users(is_deleted);
CREATE INDEX IF NOT EXISTS ix_skill_categories_parent_id ON skill_categories(parent_id);
CREATE INDEX IF NOT EXISTS ix_skill_categories_moderated_by ON skill_categories(moderated_by);
CREATE INDEX IF NOT EXISTS ix_skills_category_id ON skills(category_id);
CREATE INDEX IF NOT EXISTS ix_skills_moderated_by ON skills(moderated_by);
CREATE INDEX IF NOT EXISTS ix_user_skills_offered_skill_id ON user_skills_offered(skill_id);
CREATE INDEX IF NOT EXISTS ix_user_skills_wanted_skill_id ON user_skills_wanted(skill_id);
CREATE INDEX IF NOT EXISTS ix_exchanges_initiator_id ON exchanges(initiator_id);
CREATE INDEX IF NOT EXISTS ix_exchanges_moderated_by ON exchanges(moderated_by);
CREATE INDEX IF NOT EXISTS ix_exchange_participants_user_id ON exchange_participants(user_id);
CREATE INDEX IF NOT EXISTS ix_exchange_participants_gives_skill_id ON exchange_participants(gives_skill_id);
CREATE INDEX IF NOT EXISTS ix_exchange_participants_gets_skill_id ON exchange_participants(gets_skill_id);
CREATE INDEX IF NOT EXISTS ix_reviews_exchange_id ON reviews(exchange_id);
CREATE INDEX IF NOT EXISTS ix_reviews_reviewer_id ON reviews(reviewer_id);
CREATE INDEX IF NOT EXISTS ix_reviews_reviewed_id ON reviews(reviewed_id);
CREATE INDEX IF NOT EXISTS ix_reviews_moderated_by ON reviews(moderated_by);
CREATE INDEX IF NOT EXISTS ix_tasks_exchange_id ON tasks(exchange_id);
CREATE INDEX IF NOT EXISTS ix_tasks_assignee_id ON tasks(assignee_id);
CREATE INDEX IF NOT EXISTS ix_messages_task_id ON messages(task_id);
CREATE INDEX IF NOT EXISTS ix_messages_sender_id ON messages(sender_id);

GRANT CONNECT ON DATABASE skillshare_db TO skillshare_app;
GRANT USAGE ON SCHEMA public TO skillshare_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO skillshare_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO skillshare_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO skillshare_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO skillshare_app;
