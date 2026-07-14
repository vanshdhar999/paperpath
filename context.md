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

### API Keys configured
- ANTHROPIC_API_KEY — for paper journey restructuring and quiz generation
- SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY — Supabase project
- DATABASE_URL — Supabase Postgres pooler connection
