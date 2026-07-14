# Research App — V1 Build Reference

**Purpose of this doc:** Reference brief for AI coding agents (e.g. Claude Code) working on this project. Keep v1 crude and shippable — don't over-engineer any single piece below. Robustness is a post-v1 concern.

---

## 1. One-Line Pitch

A "Duolingo for research papers": users pick a domain and a difficulty track, work through a sequence of papers that unlock based on prerequisites, prove understanding via a short quiz, and build a public profile of papers read — a GitHub contributions graph, but for research literacy instead of code.

**Core loop:** sign up → pick domain + track → read a paper (via a structured "journey" view, not a raw PDF) → take a quiz → paper marked complete → profile updates → next paper unlocks.

---

## 2. V1 Scope — Definition of Done

Single domain only: **ML/AI**. Do not generalize to multiple domains in v1.

| # | Deliverable | Notes |
|---|---|---|
| 1 | Auth + user profile | Email/domain interests. Keep minimal. |
| 2 | Track selection | Beginner / Intermediate / Pro, ML/AI only |
| 3 | Prerequisite graph (skill tree) | ~20–30 hand-picked papers, manually seeded edges. Not auto-generated in v1. |
| 4 | Paper "journey" reading view | LLM-restructured summary + figures + inline jargon explanations, not a PDF viewer |
| 5 | Quiz generation + completion gating | Quiz auto-generated per paper; passing = paper marked "completed" |
| 6 | Public profile page | Completed papers shown, GitHub-contributions-graph style |
| 7 | Daily/weekly suggested papers | Pulled from arXiv new listings, ranked by embedding similarity to user's interests/history |

### Explicitly out of scope for v1
- Anti-gaming / quiz-integrity mechanisms (trust the user — audience is genuinely interested learners)
- Recruiter/company-facing features, hiring signal, verification badges
- Mobile apps (web only; React Native port is a later phase)
- Multiple domains beyond ML/AI
- Automated prerequisite-graph generation from citation data (v1 = manual seed; citation-graph-assisted expansion is v2)
- Social/collaborative features (comments, following, leaderboards)

---

## 3. Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | Next.js (React + TypeScript) + Tailwind CSS | Fast to ship, good defaults, deploys trivially |
| Backend | Python + FastAPI | Paper ingestion, PDF parsing, embeddings, and LLM calls are all Python-native; keeps ML-heavy logic in one place |
| Database | PostgreSQL (via Supabase) | Relational fits the prerequisite-graph + user-progress model well |
| Vector storage | `pgvector` extension on the same Postgres instance | Avoids standing up a separate vector DB for v1 |
| Auth + storage | Supabase Auth + Supabase Storage | Bundled with the DB, minimal infra for a solo build |
| LLM | Claude API (Anthropic) | Paper restructuring, quiz generation, jargon explanation |
| Embeddings | `sentence-transformers` (e.g. `all-MiniLM-L6-v2`), run locally in the FastAPI service | Free, no external API dependency, good enough for v1 relevance ranking |
| PDF parsing | PyMuPDF (`fitz`) or `pdfplumber` | Simple text + figure extraction; GROBID (structured academic parsing) is a v2 upgrade once basic extraction proves the concept |
| Scheduled jobs | A basic cron job (Render/Railway cron, or `APScheduler` in the FastAPI app) | For daily/weekly ingestion — no need for Celery/Redis at this stage |
| Hosting | Vercel (frontend) + Render or Railway (backend) + Supabase (DB/auth/storage) | Low-ops, cheap to run for a side project |

---

## 4. External Data Sources

| Source | Use | Notes |
|---|---|---|
| **arXiv API** | Primary paper content source (metadata + PDF) | Free, no auth required |
| **Semantic Scholar Graph API (S2AG)** | Citation graph, "influential citation" flags, auto-generated TLDRs | Use influential-citation flags as the strongest signal for prerequisite relationships when expanding the graph later |
| **OpenReview API** | Confirming top-tier conference acceptance (ICLR/NeurIPS) | Needed for the "top-tier conference" filter in daily/weekly suggestions — arXiv alone only tells you it's a preprint |

---

## 5. Data Model (crude v1 schema)

```
users
  id, email, name, domain_interests[], created_at

papers
  id, arxiv_id, semantic_scholar_id, title, authors,
  abstract, pdf_url, published_date, venue,
  embedding (vector), difficulty_tier [beginner|intermediate|pro]

prerequisites            -- edges of the DAG
  paper_id, prerequisite_paper_id

tracks
  id, domain, name        -- e.g. "ML/AI — Beginner"

track_papers
  track_id, paper_id, order_hint

user_progress
  user_id, paper_id, status [locked|unlocked|in_progress|completed],
  quiz_score, completed_at

quizzes
  paper_id, questions (JSON)
```

Public profile = derived view: `user_progress` where `status = completed`, joined with `papers`.

Unlock rule: a paper's status flips to `unlocked` once all rows in `prerequisites` pointing to it are `completed` for that user.

---

## 6. LLM Integration Points

All via Claude API, called from the FastAPI backend:

1. **Paper restructuring** — raw extracted text → structured sections: Problem → Prior Approaches (linked to prerequisite papers) → Method → Results → Why It Matters
2. **Inline jargon/term explanation** — short, hover-able explanations for dense terms/equations
3. **Quiz generation** — short quiz derived from the key claims in each section; this is the completion gate
4. **Relevance/difficulty tagging (stretch, not blocking v1)** — used for the daily/weekly suggestion feed if embedding similarity alone isn't precise enough

Cache LLM outputs per paper (restructured journey + quiz) — regenerate on demand only, not on every page view.

---

## 7. Suggested Build Order

1. DB schema + seed script: ~20–30 hand-picked ML/AI papers with manually drawn prerequisite edges
2. Paper ingestion script: fetch from arXiv/S2AG → extract text → generate embeddings → store
3. Basic auth + profile creation
4. Track/skill-tree UI (locked/unlocked visualization)
5. Paper journey view (LLM restructuring pipeline, cached per paper)
6. Quiz generation + completion flow
7. Public profile page
8. Daily/weekly suggestion job (cron + embedding similarity against arXiv new listings)

---

## 8. Post-V1 Ideas (context only — do not build yet)

- Citation-graph-assisted expansion of the prerequisite graph beyond the manual seed set
- GROBID-based structured PDF parsing (better figure/section extraction than PyMuPDF)
- Multi-domain support beyond ML/AI
- Recruiter/company-facing profile view, hiring-signal framing
- React Native mobile port
