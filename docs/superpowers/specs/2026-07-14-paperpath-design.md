# Paperpath — V1 Design Document

**Date:** 2026-07-14
**Status:** Approved

---

## 1. Overview

"Duolingo for research papers" — ML/AI domain only for v1. Users work through a hand-curated DAG of ~20–30 papers, prove understanding via LLM-generated quizzes, and build a public profile showing their research literacy.

**Core loop:** sign up → pick track → read paper (structured journey view) → take quiz → paper marked complete → profile updates → next paper unlocks.

---

## 2. Decisions Made

| Decision | Choice | Reason |
|---|---|---|
| Build strategy | Feature-by-feature full-stack slices (Approach A) | Always have a working app; matches "brick by brick" intent |
| Repo structure | Monorepo (`frontend/` + `backend/`) | Simpler to manage solo; atomic commits across stack |
| Backend hosting | Railway | Simple DX, free tier, good FastAPI support |
| Frontend hosting | Vercel | Native Next.js support, auto-deploy on push |
| Auth method | Supabase email magic link | No password complexity needed for v1 |
| State management | React Server Components + useState (no Redux/Zustand) | Keeps it simple |
| Styling | Tailwind, dark theme | Developer/research aesthetic |

---

## 3. Repository Structure

```
paperpath/
├── frontend/                  # Next.js 14 (App Router) + TypeScript + Tailwind
│   ├── app/
│   │   ├── (auth)/            # login, signup pages
│   │   ├── dashboard/         # track selection, skill tree
│   │   ├── paper/[id]/        # journey reading view + quiz
│   │   └── profile/[username]/ # public profile page
│   ├── components/
│   ├── lib/                   # supabase client, api helpers
│   └── .env.local
│
├── backend/                   # Python 3.11 + FastAPI
│   ├── app/
│   │   ├── api/               # route handlers
│   │   ├── services/          # claude_service, embeddings, arxiv, ingestion
│   │   ├── db/                # SQLAlchemy models + Alembic migrations
│   │   └── scheduler/         # APScheduler cron jobs
│   ├── scripts/
│   │   └── seed.py            # seeds 20–30 ML/AI papers + prerequisite edges
│   └── .env
│
├── docs/
│   └── superpowers/specs/
├── context.md
├── CLAUDE.md
└── .github/
    └── workflows/
```

---

## 4. Database Schema

```sql
-- Users (extends Supabase Auth)
users
  id UUID (FK → auth.users)
  email TEXT
  name TEXT
  username TEXT UNIQUE
  domain_interests TEXT[]
  created_at TIMESTAMPTZ

-- Papers
papers
  id UUID
  arxiv_id TEXT UNIQUE
  semantic_scholar_id TEXT
  title TEXT
  authors TEXT[]
  abstract TEXT
  pdf_url TEXT
  published_date DATE
  venue TEXT
  full_text TEXT
  journey_cache JSONB        -- cached LLM restructuring output
  quiz_cache JSONB           -- cached quiz questions
  embedding VECTOR(384)      -- all-MiniLM-L6-v2
  difficulty_tier TEXT       -- beginner | intermediate | pro
  created_at TIMESTAMPTZ

-- Prerequisite DAG edges
prerequisites
  paper_id UUID (FK → papers)
  prerequisite_paper_id UUID (FK → papers)
  PRIMARY KEY (paper_id, prerequisite_paper_id)

-- Tracks
tracks
  id UUID
  domain TEXT                -- "ML/AI" only in v1
  name TEXT                  -- "Beginner" | "Intermediate" | "Pro"

-- Papers in a track
track_papers
  track_id UUID (FK → tracks)
  paper_id UUID (FK → papers)
  order_hint INT

-- User progress
user_progress
  user_id UUID (FK → users)
  paper_id UUID (FK → papers)
  status TEXT                -- locked | unlocked | in_progress | completed
  quiz_score INT
  completed_at TIMESTAMPTZ
  PRIMARY KEY (user_id, paper_id)

-- Quizzes
quizzes
  id UUID
  paper_id UUID UNIQUE (FK → papers)
  questions JSONB            -- [{question, options[], correct_index, explanation}]
  generated_at TIMESTAMPTZ
```

**Unlock rule:** When a user completes a paper, the backend checks `prerequisites` — any paper whose all prerequisites are `completed` for that user gets flipped to `unlocked`.

---

## 5. Backend (FastAPI) Architecture

### API Routes

```
POST   /auth/sync-user          # create users row after Supabase signup
GET    /tracks                  # list all tracks
GET    /tracks/{id}/papers      # papers in track with user's unlock status
GET    /papers/{id}/journey     # LLM-restructured view (from cache)
GET    /papers/{id}/quiz        # fetch quiz questions
POST   /papers/{id}/quiz/submit # grade quiz, update progress, trigger unlocks
GET    /profile/{username}      # public profile
GET    /suggestions             # daily/weekly papers by embedding similarity
```

### Background Services

| Service | Responsibility |
|---|---|
| `ingestion_service` | arXiv fetch → PyMuPDF extraction → embedding → DB store |
| `claude_service` | Journey restructuring + quiz generation; writes to cache columns |
| `scheduler` | APScheduler nightly cron — new arXiv listings → similarity ranking → suggestions |

### Key Patterns
- All Claude API calls cached per paper — called once per paper ever, never per user request
- FastAPI dependency injection for DB session + current user (from Supabase JWT)
- `seed.py` runs ingestion + Claude pipeline on first deploy for all 20–30 seed papers

---

## 6. Frontend (Next.js) Architecture

### Pages

| Route | Content |
|---|---|
| `/` | Landing page, sign up / log in CTA |
| `/dashboard` | Track selector + skill tree DAG |
| `/paper/[id]` | Journey reading view + quiz entry |
| `/paper/[id]/quiz` | Quiz flow, grading, unlock animation |
| `/profile/[username]` | Public profile, contribution grid |

### Key Components

| Component | Description |
|---|---|
| `SkillTree` | SVG DAG — nodes colored by status (locked=grey, unlocked=blue, completed=green) |
| `PaperJourney` | Renders journey sections: Problem → Prior Art → Method → Results → Why It Matters |
| `JargonTooltip` | Hover-triggered explanation popover |
| `QuizCard` | Single question, multiple choice, immediate feedback |
| `ContributionGrid` | GitHub-style calendar heatmap of completed papers |

### Auth Flow
1. Supabase Auth email magic link
2. On first login → `POST /auth/sync-user` → creates `users` row
3. Supabase JWT passed as `Authorization: Bearer` on all FastAPI requests

---

## 7. Environment Variables

### `frontend/.env.local`
```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
```

### `backend/.env`
```
ANTHROPIC_API_KEY=
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
DATABASE_URL=postgresql://...
```

---

## 8. Build Order (8 Bricks)

| Brick | Deliverable |
|---|---|
| 1 | Monorepo scaffold + DB schema + Alembic migrations + seed script |
| 2 | Paper ingestion pipeline (arXiv → PDF → embeddings → DB) |
| 3 | Auth (magic link) + `/auth/sync-user` + dashboard shell |
| 4 | Track + skill tree UI (DAG visualization) |
| 5 | Paper journey view (Claude restructuring, cached, rendered) |
| 6 | Quiz generation + completion flow (Claude gen, grading, unlocks) |
| 7 | Public profile page (contribution grid) |
| 8 | Daily/weekly suggestion cron job |

---

## 9. API Keys Required

| Key | Source | Used for |
|---|---|---|
| `ANTHROPIC_API_KEY` | console.anthropic.com | Paper restructuring, quiz generation, jargon explanations |
| `SUPABASE_URL` | supabase.com → project settings | All Supabase operations |
| `SUPABASE_ANON_KEY` | supabase.com → project settings | Frontend queries |
| `SUPABASE_SERVICE_ROLE_KEY` | supabase.com → project settings | Backend admin operations |
| `DATABASE_URL` | supabase.com → project settings → database | Direct Postgres connection for SQLAlchemy |

No API key required for arXiv or Semantic Scholar (free, unauthenticated for v1 usage levels).

---

## 10. Out of Scope for V1

- Anti-gaming / quiz integrity
- Multiple domains beyond ML/AI
- Mobile apps
- Social features (comments, following, leaderboards)
- Automated prerequisite graph generation
- GROBID-based PDF parsing
- Recruiter-facing features
