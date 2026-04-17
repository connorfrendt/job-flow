JobFlow — Architecture Specification
System Architecture
┌─────────────────────────────────────────────────────┐
│                    Vue 3 Frontend                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │  Kanban   │ │  Job     │ │ Profile  │ │ Stats  │ │
│  │  Board    │ │  Detail  │ │ Config   │ │ Dash   │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────┘ │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP (REST)
┌──────────────────────▼──────────────────────────────┐
│                  FastAPI Backend                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │  Jobs    │ │  Parse   │ │  Adzuna  │ │ Score  │ │
│  │  CRUD    │ │  Service │ │  Ingest  │ │ Engine │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────┘ │
└──────────┬───────────┬──────────┬───────────────────┘
           │           │          │
     ┌─────▼─────┐ ┌───▼───┐ ┌───▼────┐
     │ PostgreSQL│ │Claude │ │Adzuna  │
     │           │ │  API  │ │  API   │
     └───────────┘ └───────┘ └────────┘
Directory Structure
jobflow/
├── docker-compose.yml
├── README.md
├── APP-SPEC.md
├── ARCH-SPEC.md
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/
│   │   │   └── index.js
│   │   ├── stores/            # Pinia state management
│   │   │   ├── jobStore.js
│   │   │   └── profileStore.js
│   │   ├── components/
│   │   │   ├── board/
│   │   │   │   ├── KanbanBoard.vue
│   │   │   │   ├── KanbanColumn.vue
│   │   │   │   └── JobCard.vue
│   │   │   ├── jobs/
│   │   │   │   ├── JobDetailModal.vue
│   │   │   │   ├── AddJobForm.vue
│   │   │   │   └── PasteJobInput.vue    # Layer 2
│   │   │   ├── profile/
│   │   │   │   └── ProfileConfig.vue
│   │   │   └── stats/                   # Layer 5
│   │   │       └── StatsDashboard.vue
│   │   ├── services/
│   │   │   └── api.js           # Axios/fetch wrapper
│   │   ├── utils/
│   │   │   └── constants.js     # Column definitions, etc.
│   │   └── assets/
│   │       └── styles/
│   │           └── main.css
│   └── public/
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings, env vars
│   │   ├── database.py          # SQLAlchemy engine/session
│   │   ├── models/
│   │   │   ├── job.py           # SQLAlchemy ORM model
│   │   │   └── profile.py       # User profile model
│   │   ├── schemas/
│   │   │   ├── job.py           # Pydantic request/response schemas
│   │   │   └── profile.py
│   │   ├── routers/
│   │   │   ├── jobs.py          # CRUD endpoints
│   │   │   ├── parse.py         # Layer 2: AI parsing
│   │   │   ├── ingest.py        # Layer 3: Adzuna ingestion
│   │   │   └── profile.py       # Profile management
│   │   ├── services/
│   │   │   ├── scoring.py       # Fit score + scam detection
│   │   │   ├── parser.py        # Claude API integration
│   │   │   └── adzuna.py        # Adzuna API client
│   │   └── utils/
│   │       └── helpers.py
│   └── alembic/                 # DB migrations
│       ├── alembic.ini
│       └── versions/
│
└── db/
    └── init.sql                 # Initial schema (backup to alembic)
Database Schema
jobs table
sqlCREATE TABLE jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           VARCHAR(255) NOT NULL,
    company         VARCHAR(255),
    location        VARCHAR(255),
    salary_min      INTEGER,
    salary_max      INTEGER,
    url             TEXT,
    description     TEXT,
    source          VARCHAR(50) DEFAULT 'manual',   -- 'manual' | 'adzuna' | 'paste'
    status          VARCHAR(50) DEFAULT 'new_leads', -- matches column key
    
    -- Enrichment (AI-populated)
    fit_score       INTEGER,                         -- 0-100
    fit_reasons     JSONB,                           -- [{type: 'pro'|'con', text: '...'}]
    legit_score     INTEGER,                         -- 0-100
    legit_flags     JSONB,                           -- [{level: 'green'|'yellow'|'red', text: '...'}]
    
    -- User fields
    notes           TEXT,
    contact_name    VARCHAR(255),
    contact_email   VARCHAR(255),
    follow_up_date  DATE,
    starred         BOOLEAN DEFAULT FALSE,
    
    -- Dedup and tracking
    adzuna_id       VARCHAR(100) UNIQUE,             -- for deduplication
    description_hash VARCHAR(64),                    -- for cross-posting detection
    
    -- Timestamps
    date_found      TIMESTAMP DEFAULT NOW(),
    date_applied    TIMESTAMP,
    date_updated    TIMESTAMP DEFAULT NOW(),
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_starred ON jobs(starred);
CREATE INDEX idx_jobs_adzuna_id ON jobs(adzuna_id);
CREATE INDEX idx_jobs_description_hash ON jobs(description_hash);
profile table
sqlCREATE TABLE profile (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skills          JSONB,          -- [{name: 'SQL', level: 'advanced'}, ...]
    target_titles   JSONB,          -- ['Data Engineer', 'ETL Developer', ...]
    location        VARCHAR(255),
    remote_pref     VARCHAR(50),    -- 'remote' | 'hybrid' | 'onsite' | 'any'
    salary_floor    INTEGER,
    exclusion_words JSONB,          -- ['senior', 'clearance', '10+ years']
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);
API Endpoints
Jobs (Layer 1)
GET    /api/jobs                  -- List all jobs (filterable by status, starred, search)
GET    /api/jobs/:id              -- Get single job detail
POST   /api/jobs                  -- Create job manually
PUT    /api/jobs/:id              -- Update job (including status change for drag-drop)
DELETE /api/jobs/:id              -- Delete job
PATCH  /api/jobs/:id/status       -- Quick status update (drag-drop)
PATCH  /api/jobs/:id/star         -- Toggle starred
Parse (Layer 2)
POST   /api/parse                 -- Send raw job description text, returns parsed fields
Profile (Layer 1+)
GET    /api/profile               -- Get user profile
PUT    /api/profile               -- Create or update profile
Ingest (Layer 3)
POST   /api/ingest/trigger        -- Manually trigger Adzuna pull
GET    /api/ingest/config         -- Get current search criteria
PUT    /api/ingest/config         -- Update search criteria
Stats (Layer 5)
GET    /api/stats/funnel          -- Conversion rates across stages
GET    /api/stats/activity        -- Applications over time
GET    /api/stats/skills          -- Most requested skills
Key Design Decisions

Single-user app (for now): No auth. One profile, one board. Keeps it simple. Auth can be added later if we want multi-user.
Status as string, not FK: The Kanban columns are defined as constants in the frontend and validated as an enum in the backend. Adding a new column is a code change, not a migration. This is intentional — the column set is stable and small.
JSONB for flexible fields: Skills, fit_reasons, legit_flags — these are semi-structured and change shape as we iterate. JSONB lets us evolve without migrations.
UUID primary keys: Avoids sequential ID leaking (important if we ever go multi-user) and makes dedup easier with Adzuna.
Description hash for cross-posting detection: SHA-256 hash of normalized description text. If two "different" companies post the same description, it's likely a recruiter farm or scam.
Separation of scoring from ingestion: Scoring is its own service so it can be applied to manual entries, pasted descriptions, AND Adzuna pulls. Same enrichment pipeline, multiple input sources.

Docker Compose Structure
yamlservices:
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend/src:/app/src    # hot reload
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://jobflow:jobflow@db:5432/jobflow
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - ADZUNA_APP_ID=${ADZUNA_APP_ID}
      - ADZUNA_APP_KEY=${ADZUNA_APP_KEY}
    volumes:
      - ./backend/app:/app/app     # hot reload
    depends_on:
      - db

  db:
    image: postgres:16
    environment:
      - POSTGRES_USER=jobflow
      - POSTGRES_PASSWORD=jobflow
      - POSTGRES_DB=jobflow
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql

volumes:
  pgdata:
Build Order (Step by Step)
Phase 1: Foundation

Docker compose with PostgreSQL + FastAPI + Vue scaffold
Database schema (jobs + profile tables)
Backend CRUD endpoints for jobs
Frontend Kanban board with drag-and-drop
Job detail modal (view/edit)
Add job form (manual entry)
Profile configuration page

Phase 2: Smart Input

Paste-and-parse UI component
Claude API integration for parsing
Fit scoring service
Score display on job cards

Phase 3: Automated Ingestion

Adzuna API client
Ingestion service with dedup
Search criteria configuration UI
Scheduled/manual trigger for pulls
Filter + score pipeline

Phase 4: Scam Detection

Rule-based legitimacy scoring
Legitimacy badge on cards
Flag detail view

Phase 5: Analytics

Funnel metrics endpoint + chart
Activity timeline
Skills heatmap