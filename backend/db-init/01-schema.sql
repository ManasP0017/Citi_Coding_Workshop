-- Bootstrap schema for all Lambda services
-- Runs automatically when PostgreSQL container starts for the first time

CREATE TABLE IF NOT EXISTS users (
    id         VARCHAR(36) PRIMARY KEY,
    email      VARCHAR(255) UNIQUE NOT NULL,
    password   VARCHAR(255) NOT NULL,
    name       VARCHAR(255) NOT NULL,
    role       VARCHAR(50)  NOT NULL DEFAULT 'viewer',
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS teams (
    id                     VARCHAR(36) PRIMARY KEY,
    name                   VARCHAR(255) NOT NULL,
    location               VARCHAR(255) NOT NULL DEFAULT '',
    organization_leader_id VARCHAR(36),
    description            TEXT         NOT NULL DEFAULT '',
    created_at             TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at             TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS members (
    id              VARCHAR(36)  PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    team_id         VARCHAR(36)  REFERENCES teams(id) ON DELETE SET NULL,
    role            VARCHAR(100) NOT NULL DEFAULT 'member',
    is_team_leader  BOOLEAN      NOT NULL DEFAULT FALSE,
    is_direct_staff BOOLEAN      NOT NULL DEFAULT TRUE,
    location        VARCHAR(255) NOT NULL DEFAULT '',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS achievements (
    id          VARCHAR(36)  PRIMARY KEY,
    title       VARCHAR(255) NOT NULL,
    description TEXT         NOT NULL DEFAULT '',
    team_id     VARCHAR(36)  NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    month       VARCHAR(20)  NOT NULL,
    year        INTEGER      NOT NULL,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email    ON users(email);
CREATE INDEX IF NOT EXISTS idx_members_email  ON members(email);
CREATE INDEX IF NOT EXISTS idx_members_team   ON members(team_id);
CREATE INDEX IF NOT EXISTS idx_ach_team       ON achievements(team_id);
CREATE INDEX IF NOT EXISTS idx_ach_year_month ON achievements(year, month);
