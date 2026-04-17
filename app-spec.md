JobFlow — App Specification
Overview
JobFlow is a personal job search management platform that helps job seekers track, organize, and evaluate job opportunities. It starts as a manual Kanban-style tracker and progressively adds intelligent features like job description parsing, fit scoring, scam detection, and automated job ingestion via the Adzuna API.
Target User
Any job seeker in any industry. The system is domain-agnostic — a data engineer, an English teacher, or a nurse can all use it by configuring their own profile and search criteria.
Core Concepts
User Profile
A single user's skill set, preferences, and job search criteria:

Skills: list of skills with self-assessed proficiency (e.g., "SQL: advanced", "Python: intermediate")
Target titles: job titles they're searching for (e.g., "Data Engineer", "ETL Developer")
Location preferences: city/state, remote preference, radius
Salary floor: minimum acceptable salary
Exclusion keywords: terms that disqualify a posting (e.g., "senior", "clearance required", "10+ years")

Job Card
A single job opportunity, containing:

Core fields: title, company, location, salary range, url, description, source (manual / adzuna)
Status: which Kanban column it lives in
Metadata: date_found, date_applied, date_updated
Enrichment fields (populated by AI or rules):

fit_score (0-100)
fit_reasons (array of pros/cons against user profile)
legitimacy_score (0-100)
legitimacy_flags (array of red/yellow/green signals)


User fields: notes, contact_name, contact_email, follow_up_date, starred

Kanban Columns (Pipeline Stages)

New Leads — auto-populated by Adzuna or manual add
Saved — user has flagged as interesting
Applied — application submitted
Phone Screen — first contact scheduled/completed
Interview — formal interview stage
Offer — received an offer
Rejected — didn't move forward (can come from any stage)
Archived — dismissed/not interested

Feature Layers (Build Incrementally)
Layer 1 — Manual Tracker (MVP)

Kanban board with drag-and-drop between columns
Add a job card manually via form (title, company, url, salary, location, notes)
Click a card to view/edit full details
Delete a card
Filter/search cards by keyword
Persistent storage in PostgreSQL

Layer 2 — Smart Input (AI Parse)

"Paste a job description" textarea that sends raw text to Claude API
Claude extracts: title, company, location, salary range, required skills, description summary
Auto-populates a new job card from the parsed output
User can review/edit before saving
Fit score calculated against user profile

Layer 3 — Adzuna Integration (Automated Ingestion)

User configures search criteria (keywords, location, salary, job type)
Backend hits Adzuna API on a schedule (configurable: hourly/daily)
New listings are ingested, deduplicated, and stored
Hard filters applied (salary floor, exclusion keywords, date)
AI scoring applied to remaining listings
Only top N results surface in "New Leads" column
Rest stored but hidden (accessible via "Show all" toggle)

Layer 4 — Scam Detection

Rule-based red flag scoring:

Salary abnormally high for role
Description very short or vague (<100 words)
No company name or generic company name
Contact email is gmail/yahoo (not corporate domain)
Urgency language ("start immediately", "hiring now")
Requests personal info (SSN, bank details, "pay for training")
Duplicate descriptions across many company names


Each flag adds to a suspicion score
Badge displayed on card: 🟢 Legit, 🟡 Review, 🔴 Suspicious

Layer 5 — Analytics Dashboard

Application funnel metrics (applied → screen → interview → offer conversion rates)
Average time in each stage
Jobs applied per week trend
Top skills requested across saved jobs
Salary range distribution of saved/applied jobs

Non-Functional Requirements

Dockerized (docker-compose up and it works)
Mobile-responsive (job hunting happens on phones)
Fast — board should load in under 1 second
Open source on GitHub with clear README

Tech Stack

Frontend: Vue 3 + Vite + Tailwind CSS (or similar utility-first CSS)
Backend: FastAPI (Python)
Database: PostgreSQL
AI: Claude API (via Anthropic SDK) for parsing and scoring
Job Data: Adzuna API for automated ingestion
Containerization: Docker + docker-compose