I'm building a project called JobFlow — a personal job search tracker with a Kanban board UI. Here are the full specs:

- APP-SPEC.md: ./app-spec.md
- ARCH-SPEC.md: ./arch-spec.md

## How I want to work:

1. **Step by step.** Do NOT build everything at once. Complete one step, show me what you did, and wait for my approval before moving to the next step. I want to review and tweak each piece.

2. **Build order — Phase 1 first:**
   - Step 1: Scaffold the project structure (docker-compose.yml, Dockerfiles, package.json, requirements.txt, directory structure). Don't write app code yet — just the skeleton. Show me the structure and wait for approval.
   - Step 2: Database — create the PostgreSQL schema (init.sql) and the SQLAlchemy models. Wait for approval.
   - Step 3: Backend — FastAPI app with CRUD endpoints for jobs (list, get, create, update, delete, status change, star toggle). Wait for approval.
   - Step 4: Frontend — Vue 3 + Vite scaffold with router, Pinia stores, and the Kanban board layout (columns render, but no real data yet — use mock data). Wait for approval.
   - Step 5: Wire it up — connect frontend to backend API, replace mock data with real API calls, drag-and-drop updates status via PATCH. Wait for approval.
   - Step 6: Job detail modal — click a card, see full details, edit fields, save. Wait for approval.
   - Step 7: Add job form — manual entry form to create a new job card. Wait for approval.
   - Step 8: Profile page — configure skills, target titles, location, salary floor, exclusion words. Wait for approval.

3. **Tech stack:**
   - Frontend: Vue 3 + Vite + Pinia + Vue Router
   - Styling: Tailwind CSS
   - Backend: FastAPI + SQLAlchemy + Alembic
   - Database: PostgreSQL 16
   - Containerization: Docker + docker-compose
   - No authentication (single-user app for now)

4. **Code style preferences:**
   - Clean, readable code with comments on non-obvious logic
   - Composition API for Vue (setup script syntax)
   - Pydantic models for all FastAPI request/response schemas
   - Async endpoints in FastAPI where appropriate
   - Use UUID primary keys everywhere

5. **When you finish each step:**
   - Tell me what you built
   - Tell me how to run/test it
   - Ask if I want to tweak anything before moving on

Start with Step 1: project scaffold and directory structure.