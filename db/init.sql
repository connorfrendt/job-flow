CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE jobs (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title            VARCHAR(255) NOT NULL,
    company          VARCHAR(255),
    location         VARCHAR(255),
    salary_min       INTEGER,
    salary_max       INTEGER,
    url              TEXT,
    description      TEXT,
    source           VARCHAR(50) DEFAULT 'manual',
    status           VARCHAR(50) DEFAULT 'new_leads',

    -- AI enrichment
    fit_score        INTEGER,
    fit_reasons      JSONB,
    legit_score      INTEGER,
    legit_flags      JSONB,

    -- User fields
    notes            TEXT,
    contact_name     VARCHAR(255),
    contact_email    VARCHAR(255),
    follow_up_date   DATE,
    starred          BOOLEAN DEFAULT FALSE,

    -- Dedup and tracking
    adzuna_id        VARCHAR(100) UNIQUE,
    description_hash VARCHAR(64),

    -- Timestamps
    date_found       TIMESTAMP DEFAULT NOW(),
    date_applied     TIMESTAMP,
    date_updated     TIMESTAMP DEFAULT NOW(),
    created_at       TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_starred ON jobs(starred);
CREATE INDEX idx_jobs_adzuna_id ON jobs(adzuna_id);
CREATE INDEX idx_jobs_description_hash ON jobs(description_hash);

CREATE TABLE profile (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skills          JSONB,
    target_titles   JSONB,
    location        VARCHAR(255),
    remote_pref     VARCHAR(50),
    salary_floor    INTEGER,
    exclusion_words JSONB,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);
