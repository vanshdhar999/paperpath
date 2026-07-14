# Paperpath — Build Context

## 2026-07-14

### Brick 1: Monorepo Scaffold + DB Schema + Seed Data ✓
- Monorepo: `frontend/` (Next.js 14) + `backend/` (FastAPI)
- DB schema: 7 tables via Alembic migration (001_initial_schema)
- Seed: 25 ML/AI papers, 3 tracks, 23 prerequisite edges, 25 track assignments
- Papers span beginner (Word2Vec → Transformers → GAN → DDPM) through
  intermediate (BERT, GPT-3, CLIP, LoRA, LDM) to pro (InstructGPT, DPO, Mamba, LLaMA)
- Frontend: Next.js 14 placeholder running on :3000
- Backend: FastAPI health endpoint running on :8000
- Next: Brick 2 — paper ingestion pipeline (arXiv fetch → PDF parse → embeddings)

### Brick 2: Paper Ingestion Pipeline ✓
- Pipeline: arXiv API → PDF download → PyMuPDF text extraction → sentence-transformer embeddings
- Services: arxiv_service, pdf_service, embedding_service, ingestion_service
- All 25 papers ingested with full_text and 384-dim embeddings
- CLI: `cd backend && .venv/bin/python -m scripts.ingest`
- Next: Brick 3 — Auth (Supabase magic link) + dashboard shell

### Brick 3: Auth (Supabase Magic Link) + Dashboard Shell ✓
- Supabase Auth with email magic link (login + signup pages)
- Auth callback route exchanges code for session, syncs user to backend DB
- Dashboard page with track selection grid
- apiFetch helper with Bearer token injection from Supabase session

### Brick 4: Track View + Skill Tree ✓
- Track detail page with SkillTree canvas-based DAG visualization
- Color-coded nodes: locked (gray), unlocked (blue), in-progress (yellow), completed (green)
- Prerequisite-based unlock logic computed server-side
- Clicking unlocked/in-progress nodes navigates to paper journey

### Brick 5: Paper Journey (LLM-Powered Reading) ✓
- Claude API restructures papers into 5 sections: problem, prior approaches, method, results, why it matters
- Jargon extraction with hover tooltips (JargonTooltip component)
- PaperJourney component renders full reading experience
- Results cached in DB to avoid redundant LLM calls

### Brick 6: Quiz System ✓
- Claude API generates 5 multiple-choice questions per paper
- QuizCard component with answer selection and feedback
- 3/5 pass threshold — passing marks paper completed, unlocks prerequisites
- Quiz results cached; progress tracked in UserProgress table

### Brick 7: Public Profile + Contribution Grid ✓
- Public profile page at /profile/[username]
- GitHub-style 365-day contribution grid (ContributionGrid component)
- Stats: total completed, beginner/intermediate/pro breakdown
- Completed papers list with scores and dates

### Brick 8: Suggestions + Nightly Scheduler ✓
- GET /suggestions endpoint using pgvector cosine distance
- Computes centroid of user's completed paper embeddings
- Ranks uncompleted papers by similarity; falls back to beginner papers
- APScheduler nightly job (03:00) fetches recent ML/AI papers from arXiv
- Suggestions displayed on dashboard with match percentage
- FastAPI lifespan hooks start/stop the scheduler

### API Keys configured
- ANTHROPIC_API_KEY — for paper journey restructuring and quiz generation
- SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY — Supabase project
- DATABASE_URL — Supabase Postgres pooler connection
