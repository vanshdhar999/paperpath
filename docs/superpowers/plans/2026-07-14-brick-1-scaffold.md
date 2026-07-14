# Brick 1: Monorepo Scaffold + DB Schema + Seed Data

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the full monorepo structure, define the database schema via Alembic migrations, and seed 25 hand-picked ML/AI papers with prerequisite edges and track assignments — all committed and pushed to GitHub.

**Architecture:** Monorepo with `frontend/` (Next.js 14) and `backend/` (FastAPI + SQLAlchemy + Alembic). The backend connects to Supabase Postgres. Seed script populates all static data (papers, tracks, prerequisites) but does NOT run ingestion or LLM calls — those are Brick 2.

**Tech Stack:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Python 3.11, FastAPI, SQLAlchemy 2.0 (sync), Alembic, psycopg2-binary, pgvector, Supabase Postgres

## Global Constraints

- Python 3.11+
- Node.js 20+
- Next.js 14 with App Router (not Pages Router)
- SQLAlchemy 2.0 synchronous sessions
- pgvector extension enabled on Supabase Postgres
- All env vars loaded from `.env` (backend) and `.env.local` (frontend) — never hardcoded
- Every task ends with `git add <files> && git commit -m "..." && git push`

---

## Prerequisites (Manual — do before running any task)

1. Go to **supabase.com** → New Project → name it `paperpath`
2. Wait for project to provision (~2 min)
3. Go to **Project Settings → Database** → copy the **Connection String (URI)** (use "Session mode" / port 5432 URI) — this is your `DATABASE_URL`
4. Go to **Project Settings → API** → copy:
   - `Project URL` → `SUPABASE_URL`
   - `anon public` key → `SUPABASE_ANON_KEY`
   - `service_role secret` key → `SUPABASE_SERVICE_ROLE_KEY`
5. Go to **SQL Editor** in Supabase → run: `CREATE EXTENSION IF NOT EXISTS vector;`
6. Have your `ANTHROPIC_API_KEY` ready (from console.anthropic.com)

---

## File Map

```
paperpath/
├── .gitignore                          CREATE
├── context.md                          CREATE
├── frontend/
│   ├── package.json                    CREATE
│   ├── next.config.js                  CREATE
│   ├── tailwind.config.ts              CREATE
│   ├── postcss.config.js               CREATE
│   ├── tsconfig.json                   CREATE
│   ├── .env.local                      CREATE (gitignored)
│   └── app/
│       ├── layout.tsx                  CREATE
│       └── page.tsx                    CREATE
└── backend/
    ├── requirements.txt                CREATE
    ├── .env                            CREATE (gitignored)
    ├── alembic.ini                     CREATE
    ├── alembic/
    │   ├── env.py                      CREATE
    │   └── versions/
    │       └── 001_initial_schema.py   CREATE
    ├── app/
    │   ├── __init__.py                 CREATE
    │   ├── main.py                     CREATE
    │   ├── config.py                   CREATE
    │   └── db/
    │       ├── __init__.py             CREATE
    │       ├── models.py               CREATE
    │       └── session.py              CREATE
    └── scripts/
        └── seed.py                     CREATE
```

---

## Task 1: Root Scaffold + .gitignore + context.md

**Files:**
- Create: `.gitignore`
- Create: `context.md`

- [ ] **Step 1: Create .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
.venv/
venv/
*.egg-info/
.env

# Node
node_modules/
.next/
.env.local
.env*.local

# OS
.DS_Store

# IDE
.idea/
.vscode/

# Misc
*.log
```

- [ ] **Step 2: Create context.md**

```markdown
# Paperpath — Build Context

## 2026-07-14

### Brick 1: Monorepo Scaffold + DB Schema + Seed Data
- Status: IN PROGRESS
- Repo: https://github.com/vanshdhar999/paperpath
- Design doc: docs/superpowers/specs/2026-07-14-paperpath-design.md
```

- [ ] **Step 3: Commit**

```bash
git add .gitignore context.md
git commit -m "feat: add .gitignore and context.md"
git push
```

---

## Task 2: Backend — requirements.txt + config + FastAPI skeleton

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/.env`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/main.py`

- [ ] **Step 1: Create backend/requirements.txt**

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy==2.0.30
psycopg2-binary==2.9.9
alembic==1.13.1
pgvector==0.2.5
python-dotenv==1.0.1
pydantic-settings==2.2.1
httpx==0.27.0
anthropic==0.28.0
sentence-transformers==2.7.0
pymupdf==1.24.4
arxiv==2.1.0
apscheduler==3.10.4
```

- [ ] **Step 2: Create backend/.env (fill in your values)**

```
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
DATABASE_URL=postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres
```

- [ ] **Step 3: Create backend/app/__init__.py**

```python
```
(empty file)

- [ ] **Step 4: Create backend/app/config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str
    supabase_url: str
    supabase_service_role_key: str
    database_url: str

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 5: Create backend/app/main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Paperpath API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 6: Install dependencies**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

- [ ] **Step 7: Verify FastAPI starts**

```bash
cd backend
uvicorn app.main:app --reload
```

Expected: `Uvicorn running on http://127.0.0.1:8000`
Open http://127.0.0.1:8000/health — should return `{"status":"ok"}`

Stop the server (Ctrl+C).

- [ ] **Step 8: Commit**

```bash
git add backend/requirements.txt backend/app/
git commit -m "feat: add FastAPI skeleton with health endpoint"
git push
```

---

## Task 3: Database Models (SQLAlchemy)

**Files:**
- Create: `backend/app/db/__init__.py`
- Create: `backend/app/db/models.py`
- Create: `backend/app/db/session.py`

**Produces:**
- `Base` — SQLAlchemy declarative base, imported by Alembic env.py
- `User`, `Paper`, `Prerequisite`, `Track`, `TrackPaper`, `UserProgress`, `Quiz` — ORM models

- [ ] **Step 1: Create backend/app/db/__init__.py**

```python
```
(empty file)

- [ ] **Step 2: Create backend/app/db/session.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 3: Create backend/app/db/models.py**

```python
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, ARRAY, DateTime, Date, Integer,
    ForeignKey, UniqueConstraint, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email = Column(String, nullable=False)
    name = Column(String)
    username = Column(String, unique=True)
    domain_interests = Column(ARRAY(String), default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    progress = relationship("UserProgress", back_populates="user")


class Paper(Base):
    __tablename__ = "papers"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    arxiv_id = Column(String, unique=True, nullable=False)
    semantic_scholar_id = Column(String)
    title = Column(Text, nullable=False)
    authors = Column(ARRAY(String), default=list)
    abstract = Column(Text)
    pdf_url = Column(String)
    published_date = Column(Date)
    venue = Column(String)
    full_text = Column(Text)
    journey_cache = Column(JSON)
    quiz_cache = Column(JSON)
    embedding = Column(Vector(384))
    difficulty_tier = Column(String, nullable=False)  # beginner|intermediate|pro
    created_at = Column(DateTime, default=datetime.utcnow)

    prerequisites = relationship(
        "Prerequisite", foreign_keys="Prerequisite.paper_id", back_populates="paper"
    )
    required_by = relationship(
        "Prerequisite", foreign_keys="Prerequisite.prerequisite_paper_id",
        back_populates="prerequisite_paper"
    )
    progress = relationship("UserProgress", back_populates="paper")
    quiz = relationship("Quiz", back_populates="paper", uselist=False)


class Prerequisite(Base):
    __tablename__ = "prerequisites"

    paper_id = Column(UUID(as_uuid=False), ForeignKey("papers.id"), primary_key=True)
    prerequisite_paper_id = Column(UUID(as_uuid=False), ForeignKey("papers.id"), primary_key=True)

    paper = relationship("Paper", foreign_keys=[paper_id], back_populates="prerequisites")
    prerequisite_paper = relationship(
        "Paper", foreign_keys=[prerequisite_paper_id], back_populates="required_by"
    )


class Track(Base):
    __tablename__ = "tracks"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    domain = Column(String, nullable=False)  # "ML/AI"
    name = Column(String, nullable=False)    # "Beginner" | "Intermediate" | "Pro"

    track_papers = relationship("TrackPaper", back_populates="track")


class TrackPaper(Base):
    __tablename__ = "track_papers"

    track_id = Column(UUID(as_uuid=False), ForeignKey("tracks.id"), primary_key=True)
    paper_id = Column(UUID(as_uuid=False), ForeignKey("papers.id"), primary_key=True)
    order_hint = Column(Integer, default=0)

    track = relationship("Track", back_populates="track_papers")
    paper = relationship("Paper")


class UserProgress(Base):
    __tablename__ = "user_progress"

    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), primary_key=True)
    paper_id = Column(UUID(as_uuid=False), ForeignKey("papers.id"), primary_key=True)
    status = Column(String, default="locked")  # locked|unlocked|in_progress|completed
    quiz_score = Column(Integer)
    completed_at = Column(DateTime)

    user = relationship("User", back_populates="progress")
    paper = relationship("Paper", back_populates="progress")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    paper_id = Column(UUID(as_uuid=False), ForeignKey("papers.id"), unique=True, nullable=False)
    questions = Column(JSON, nullable=False)  # [{question, options[], correct_index, explanation}]
    generated_at = Column(DateTime, default=datetime.utcnow)

    paper = relationship("Paper", back_populates="quiz")
```

- [ ] **Step 4: Verify models import cleanly**

```bash
cd backend
python -c "from app.db.models import Base, Paper, User, Track; print('Models OK')"
```

Expected: `Models OK`

- [ ] **Step 5: Commit**

```bash
git add backend/app/db/
git commit -m "feat: add SQLAlchemy models for all DB tables"
git push
```

---

## Task 4: Alembic Setup + Initial Migration

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/versions/001_initial_schema.py`

- [ ] **Step 1: Initialise Alembic**

```bash
cd backend
alembic init alembic
```

This creates `alembic/` directory and `alembic.ini`. We will overwrite env.py next.

- [ ] **Step 2: Update alembic.ini — set sqlalchemy.url placeholder**

In `backend/alembic.ini`, find the line:
```
sqlalchemy.url = driver://user:pass@localhost/dbname
```
Replace it with:
```
sqlalchemy.url = placeholder_overridden_in_env_py
```

- [ ] **Step 3: Overwrite backend/alembic/env.py**

```python
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

load_dotenv()

config = context.config
fileConfig(config.config_file_name)

# Override sqlalchemy.url from environment
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

# Import all models so Alembic can detect them
from app.db.models import Base  # noqa: E402
target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 4: Create backend/alembic/versions/001_initial_schema.py**

```python
"""Initial schema

Revision ID: 001
Create Date: 2026-07-14
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Enable pgvector (must be done in Supabase SQL editor first, but safe to re-run)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("email", sa.String, nullable=False),
        sa.Column("name", sa.String),
        sa.Column("username", sa.String, unique=True),
        sa.Column("domain_interests", sa.ARRAY(sa.String), default=list),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "papers",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("arxiv_id", sa.String, unique=True, nullable=False),
        sa.Column("semantic_scholar_id", sa.String),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("authors", sa.ARRAY(sa.String)),
        sa.Column("abstract", sa.Text),
        sa.Column("pdf_url", sa.String),
        sa.Column("published_date", sa.Date),
        sa.Column("venue", sa.String),
        sa.Column("full_text", sa.Text),
        sa.Column("journey_cache", sa.JSON),
        sa.Column("quiz_cache", sa.JSON),
        sa.Column("embedding", Vector(384)),
        sa.Column("difficulty_tier", sa.String, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "prerequisites",
        sa.Column("paper_id", UUID(as_uuid=False), sa.ForeignKey("papers.id"), primary_key=True),
        sa.Column("prerequisite_paper_id", UUID(as_uuid=False), sa.ForeignKey("papers.id"), primary_key=True),
    )

    op.create_table(
        "tracks",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("domain", sa.String, nullable=False),
        sa.Column("name", sa.String, nullable=False),
    )

    op.create_table(
        "track_papers",
        sa.Column("track_id", UUID(as_uuid=False), sa.ForeignKey("tracks.id"), primary_key=True),
        sa.Column("paper_id", UUID(as_uuid=False), sa.ForeignKey("papers.id"), primary_key=True),
        sa.Column("order_hint", sa.Integer, default=0),
    )

    op.create_table(
        "user_progress",
        sa.Column("user_id", UUID(as_uuid=False), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("paper_id", UUID(as_uuid=False), sa.ForeignKey("papers.id"), primary_key=True),
        sa.Column("status", sa.String, default="locked"),
        sa.Column("quiz_score", sa.Integer),
        sa.Column("completed_at", sa.DateTime),
    )

    op.create_table(
        "quizzes",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("paper_id", UUID(as_uuid=False), sa.ForeignKey("papers.id"), unique=True, nullable=False),
        sa.Column("questions", sa.JSON, nullable=False),
        sa.Column("generated_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("quizzes")
    op.drop_table("user_progress")
    op.drop_table("track_papers")
    op.drop_table("tracks")
    op.drop_table("prerequisites")
    op.drop_table("papers")
    op.drop_table("users")
```

- [ ] **Step 5: Run migration against Supabase**

```bash
cd backend
alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial schema
```

- [ ] **Step 6: Verify tables exist in Supabase**

Go to Supabase → Table Editor — you should see: `users`, `papers`, `prerequisites`, `tracks`, `track_papers`, `user_progress`, `quizzes`.

- [ ] **Step 7: Commit**

```bash
git add backend/alembic.ini backend/alembic/
git commit -m "feat: add Alembic setup and initial DB schema migration"
git push
```

---

## Task 5: Seed Script (25 ML/AI Papers + Tracks + Prerequisites)

**Files:**
- Create: `backend/scripts/__init__.py`
- Create: `backend/scripts/seed.py`

**What this does:** Inserts 3 tracks (Beginner/Intermediate/Pro), 25 hand-picked ML/AI papers with metadata, prerequisite DAG edges, and track assignments. Does NOT fetch PDFs or generate embeddings (Brick 2).

- [ ] **Step 1: Create backend/scripts/__init__.py**

```python
```
(empty file)

- [ ] **Step 2: Create backend/scripts/seed.py**

```python
"""
Seed script: inserts 3 tracks + 25 ML/AI papers + prerequisite edges + track assignments.
Run from backend/ directory: python -m scripts.seed
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from dotenv import load_dotenv
load_dotenv()

from app.db.session import SessionLocal
from app.db.models import Paper, Track, TrackPaper, Prerequisite


# ── Stable UUIDs keyed by arxiv_id ──────────────────────────────────────────
def uid(arxiv_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"paperpath:paper:{arxiv_id}"))


PAPERS = [
    # ── BEGINNER ────────────────────────────────────────────────────────────
    {
        "id": uid("1301.3781"),
        "arxiv_id": "1301.3781",
        "title": "Efficient Estimation of Word Representations in Vector Space",
        "authors": ["Tomas Mikolov", "Kai Chen", "Greg Corrado", "Jeffrey Dean"],
        "abstract": (
            "Introduces Word2Vec — shallow neural networks that learn dense word "
            "embeddings from raw text. Foundational for all subsequent representation learning."
        ),
        "pdf_url": "https://arxiv.org/pdf/1301.3781",
        "difficulty_tier": "beginner",
        "venue": "ICLR 2013",
    },
    {
        "id": uid("1412.6980"),
        "arxiv_id": "1412.6980",
        "title": "Adam: A Method for Stochastic Optimization",
        "authors": ["Diederik P. Kingma", "Jimmy Ba"],
        "abstract": (
            "Introduces Adam optimizer combining momentum and adaptive learning rates. "
            "The default optimizer for training deep neural networks."
        ),
        "pdf_url": "https://arxiv.org/pdf/1412.6980",
        "difficulty_tier": "beginner",
        "venue": "ICLR 2015",
    },
    {
        "id": uid("1502.03167"),
        "arxiv_id": "1502.03167",
        "title": "Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift",
        "authors": ["Sergey Ioffe", "Christian Szegedy"],
        "abstract": (
            "Batch normalization normalizes layer inputs to stabilize and accelerate training. "
            "Became a standard component in deep networks."
        ),
        "pdf_url": "https://arxiv.org/pdf/1502.03167",
        "difficulty_tier": "beginner",
        "venue": "ICML 2015",
    },
    {
        "id": uid("1512.03385"),
        "arxiv_id": "1512.03385",
        "title": "Deep Residual Learning for Image Recognition",
        "authors": ["Kaiming He", "Xiangyu Zhang", "Shaoqing Ren", "Jian Sun"],
        "abstract": (
            "ResNet introduces skip connections to train very deep networks (100+ layers). "
            "Won ImageNet 2015 and remains a backbone architecture."
        ),
        "pdf_url": "https://arxiv.org/pdf/1512.03385",
        "difficulty_tier": "beginner",
        "venue": "CVPR 2016",
    },
    {
        "id": uid("1406.2661"),
        "arxiv_id": "1406.2661",
        "title": "Generative Adversarial Nets",
        "authors": ["Ian J. Goodfellow", "Jean Pouget-Abadie", "Mehdi Mirza",
                    "Bing Xu", "David Warde-Farley", "Sherjil Ozair",
                    "Aaron Courville", "Yoshua Bengio"],
        "abstract": (
            "Introduces GANs — a generator and discriminator trained adversarially. "
            "Foundational paper for generative modelling."
        ),
        "pdf_url": "https://arxiv.org/pdf/1406.2661",
        "difficulty_tier": "beginner",
        "venue": "NeurIPS 2014",
    },
    {
        "id": uid("1706.03762"),
        "arxiv_id": "1706.03762",
        "title": "Attention Is All You Need",
        "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar",
                    "Jakob Uszkoreit", "Llion Jones", "Aidan N. Gomez",
                    "Lukasz Kaiser", "Illia Polosukhin"],
        "abstract": (
            "Introduces the Transformer architecture based entirely on self-attention. "
            "The foundation of BERT, GPT, and all modern LLMs."
        ),
        "pdf_url": "https://arxiv.org/pdf/1706.03762",
        "difficulty_tier": "beginner",
        "venue": "NeurIPS 2017",
    },
    {
        "id": uid("2006.11239"),
        "arxiv_id": "2006.11239",
        "title": "Denoising Diffusion Probabilistic Models",
        "authors": ["Jonathan Ho", "Ajay Jain", "Pieter Abbeel"],
        "abstract": (
            "DDPM formalises diffusion as a Markov chain of noising/denoising steps. "
            "The probabilistic backbone of Stable Diffusion and DALL-E 2."
        ),
        "pdf_url": "https://arxiv.org/pdf/2006.11239",
        "difficulty_tier": "beginner",
        "venue": "NeurIPS 2020",
    },
    # ── INTERMEDIATE ────────────────────────────────────────────────────────
    {
        "id": uid("1810.04805"),
        "arxiv_id": "1810.04805",
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "authors": ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
        "abstract": (
            "BERT pre-trains a bidirectional Transformer on masked language modelling. "
            "Fine-tuning BERT achieves SOTA on 11 NLP tasks."
        ),
        "pdf_url": "https://arxiv.org/pdf/1810.04805",
        "difficulty_tier": "intermediate",
        "venue": "NAACL 2019",
    },
    {
        "id": uid("1907.11692"),
        "arxiv_id": "1907.11692",
        "title": "RoBERTa: A Robustly Optimized BERT Pretraining Approach",
        "authors": ["Yinhan Liu", "Myle Ott", "Naman Goyal", "Jingfei Du",
                    "Mandar Joshi", "Danqi Chen", "Omer Levy", "Mike Lewis",
                    "Luke Zettlemoyer", "Veselin Stoyanov"],
        "abstract": (
            "Shows BERT was significantly undertrained. RoBERTa trains longer, on more data, "
            "with larger batches, outperforming BERT on all benchmarks."
        ),
        "pdf_url": "https://arxiv.org/pdf/1907.11692",
        "difficulty_tier": "intermediate",
        "venue": "arXiv 2019",
    },
    {
        "id": uid("1910.10683"),
        "arxiv_id": "1910.10683",
        "title": "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer",
        "authors": ["Colin Raffel", "Noam Shazeer", "Adam Roberts", "Katherine Lee",
                    "Sharan Narang", "Michael Matena", "Yanqi Zhou", "Wei Li", "Peter J. Liu"],
        "abstract": (
            "T5 frames every NLP task as text-to-text. Comprehensive study of transfer learning "
            "at scale using the C4 dataset."
        ),
        "pdf_url": "https://arxiv.org/pdf/1910.10683",
        "difficulty_tier": "intermediate",
        "venue": "JMLR 2020",
    },
    {
        "id": uid("2010.11929"),
        "arxiv_id": "2010.11929",
        "title": "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
        "authors": ["Alexey Dosovitskiy", "Lucas Beyer", "Alexander Kolesnikov",
                    "Dirk Weissenborn", "Xiaohua Zhai", "Thomas Unterthiner",
                    "Mostafa Dehghani", "Matthias Minderer", "Georg Heigold",
                    "Sylvain Gelly", "Jakob Uszkoreit", "Neil Houlsby"],
        "abstract": (
            "ViT applies a pure Transformer to image patches, showing that CNNs are not "
            "necessary when training on large datasets."
        ),
        "pdf_url": "https://arxiv.org/pdf/2010.11929",
        "difficulty_tier": "intermediate",
        "venue": "ICLR 2021",
    },
    {
        "id": uid("2005.14165"),
        "arxiv_id": "2005.14165",
        "title": "Language Models are Few-Shot Learners",
        "authors": ["Tom B. Brown", "Benjamin Mann", "Nick Ryder"],
        "abstract": (
            "GPT-3: a 175B parameter autoregressive language model demonstrating in-context "
            "learning — new tasks from a few examples in the prompt alone."
        ),
        "pdf_url": "https://arxiv.org/pdf/2005.14165",
        "difficulty_tier": "intermediate",
        "venue": "NeurIPS 2020",
    },
    {
        "id": uid("2001.08361"),
        "arxiv_id": "2001.08361",
        "title": "Scaling Laws for Neural Language Models",
        "authors": ["Jared Kaplan", "Sam McCandlish", "Tom Henighan",
                    "Tom B. Brown", "Benjamin Chess", "Rewon Child",
                    "Scott Gray", "Alec Radford", "Jeffrey Wu", "Dario Amodei"],
        "abstract": (
            "Empirical study showing loss scales as a power law with model size, "
            "dataset size, and compute. Guides how to allocate budgets for LLM training."
        ),
        "pdf_url": "https://arxiv.org/pdf/2001.08361",
        "difficulty_tier": "intermediate",
        "venue": "arXiv 2020",
    },
    {
        "id": uid("2103.00020"),
        "arxiv_id": "2103.00020",
        "title": "Learning Transferable Visual Models From Natural Language Supervision",
        "authors": ["Alec Radford", "Jong Wook Kim", "Chris Hallacy",
                    "Aditya Ramesh", "Gabriel Goh", "Sandhini Agarwal",
                    "Girish Sastry", "Amanda Askell", "Pamela Mishkin",
                    "Jack Clark", "Gretchen Krueger", "Ilya Sutskever"],
        "abstract": (
            "CLIP trains a vision encoder and text encoder jointly via contrastive learning on "
            "400M image-text pairs. Enables zero-shot image classification."
        ),
        "pdf_url": "https://arxiv.org/pdf/2103.00020",
        "difficulty_tier": "intermediate",
        "venue": "ICML 2021",
    },
    {
        "id": uid("2106.09685"),
        "arxiv_id": "2106.09685",
        "title": "LoRA: Low-Rank Adaptation of Large Language Models",
        "authors": ["Edward J. Hu", "Yelong Shen", "Phillip Wallis", "Zeyuan Allen-Zhu",
                    "Yuanzhi Li", "Shean Wang", "Lu Wang", "Weizhu Chen"],
        "abstract": (
            "LoRA freezes pre-trained weights and injects trainable low-rank matrices. "
            "Reduces fine-tuning parameters by 10,000x with no quality loss."
        ),
        "pdf_url": "https://arxiv.org/pdf/2106.09685",
        "difficulty_tier": "intermediate",
        "venue": "ICLR 2022",
    },
    {
        "id": uid("2112.10752"),
        "arxiv_id": "2112.10752",
        "title": "High-Resolution Image Synthesis with Latent Diffusion Models",
        "authors": ["Robin Rombach", "Andreas Blattmann", "Dominik Lorenz",
                    "Patrick Esser", "Björn Ommer"],
        "abstract": (
            "Latent Diffusion Models (Stable Diffusion) run the diffusion process in a "
            "compressed latent space, enabling high-res image synthesis at low compute."
        ),
        "pdf_url": "https://arxiv.org/pdf/2112.10752",
        "difficulty_tier": "intermediate",
        "venue": "CVPR 2022",
    },
    {
        "id": uid("2204.06125"),
        "arxiv_id": "2204.06125",
        "title": "Hierarchical Text-Conditional Image Generation with CLIP Latents",
        "authors": ["Aditya Ramesh", "Prafulla Dhariwal", "Alex Nichol",
                    "Casey Chu", "Mark Chen"],
        "abstract": (
            "DALL-E 2 uses a CLIP prior to map text embeddings to image embeddings, "
            "then a diffusion decoder. Achieves photorealistic text-to-image synthesis."
        ),
        "pdf_url": "https://arxiv.org/pdf/2204.06125",
        "difficulty_tier": "intermediate",
        "venue": "arXiv 2022",
    },
    # ── PRO ─────────────────────────────────────────────────────────────────
    {
        "id": uid("2203.02155"),
        "arxiv_id": "2203.02155",
        "title": "Training language models to follow instructions with human feedback",
        "authors": ["Long Ouyang", "Jeffrey Wu", "Xu Jiang"],
        "abstract": (
            "InstructGPT: fine-tunes GPT-3 with RLHF to follow instructions, "
            "showing aligned models preferred over larger unaligned ones."
        ),
        "pdf_url": "https://arxiv.org/pdf/2203.02155",
        "difficulty_tier": "pro",
        "venue": "NeurIPS 2022",
    },
    {
        "id": uid("2201.11903"),
        "arxiv_id": "2201.11903",
        "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
        "authors": ["Jason Wei", "Xuezhi Wang", "Dale Schuurmans",
                    "Maarten Bosma", "Brian Ichter", "Fei Xia",
                    "Ed Chi", "Quoc Le", "Denny Zhou"],
        "abstract": (
            "Shows that prompting LLMs with step-by-step reasoning examples (chain-of-thought) "
            "dramatically improves performance on arithmetic, commonsense, and symbolic tasks."
        ),
        "pdf_url": "https://arxiv.org/pdf/2201.11903",
        "difficulty_tier": "pro",
        "venue": "NeurIPS 2022",
    },
    {
        "id": uid("2203.15556"),
        "arxiv_id": "2203.15556",
        "title": "Training Compute-Optimal Large Language Models",
        "authors": ["Jordan Hoffmann", "Sebastian Borgeaud", "Arthur Mensch"],
        "abstract": (
            "Chinchilla: shows GPT-3-class models are undertrained. Optimal scaling "
            "allocates equal budget to model size and token count."
        ),
        "pdf_url": "https://arxiv.org/pdf/2203.15556",
        "difficulty_tier": "pro",
        "venue": "NeurIPS 2022",
    },
    {
        "id": uid("2205.14135"),
        "arxiv_id": "2205.14135",
        "title": "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness",
        "authors": ["Tri Dao", "Daniel Y. Fu", "Stefano Ermon", "Atri Rudra", "Christopher Ré"],
        "abstract": (
            "FlashAttention rewrites attention computation to be IO-aware, reducing memory "
            "from O(N²) to O(N) and speeding up Transformer training 2-4x."
        ),
        "pdf_url": "https://arxiv.org/pdf/2205.14135",
        "difficulty_tier": "pro",
        "venue": "NeurIPS 2022",
    },
    {
        "id": uid("2302.13971"),
        "arxiv_id": "2302.13971",
        "title": "LLaMA: Open and Efficient Foundation Language Models",
        "authors": ["Hugo Touvron", "Thibaut Lavril", "Gautier Izacard",
                    "Xavier Martinet", "Marie-Anne Lachaux", "Timothée Lacroix",
                    "Baptiste Rozière", "Naman Goyal", "Eric Hambro",
                    "Faisal Azhar", "Aurelien Rodriguez", "Armand Joulin",
                    "Edouard Grave", "Guillaume Lample"],
        "abstract": (
            "LLaMA releases open foundation models (7B–65B) trained on public data only. "
            "Outperforms GPT-3 on most benchmarks at 13B parameters."
        ),
        "pdf_url": "https://arxiv.org/pdf/2302.13971",
        "difficulty_tier": "pro",
        "venue": "arXiv 2023",
    },
    {
        "id": uid("2212.08073"),
        "arxiv_id": "2212.08073",
        "title": "Constitutional AI: Harmlessness from AI Feedback",
        "authors": ["Yuntao Bai", "Saurav Kadavath", "Sandipan Kundu"],
        "abstract": (
            "Constitutional AI trains a model to critique and revise its own outputs "
            "using a set of principles, reducing reliance on human labellers for harmlessness."
        ),
        "pdf_url": "https://arxiv.org/pdf/2212.08073",
        "difficulty_tier": "pro",
        "venue": "arXiv 2022",
    },
    {
        "id": uid("2305.18290"),
        "arxiv_id": "2305.18290",
        "title": "Direct Preference Optimization: Your Language Model is Secretly a Reward Model",
        "authors": ["Rafael Rafailov", "Archit Sharma", "Eric Mitchell",
                    "Stefano Ermon", "Christopher D. Manning", "Chelsea Finn"],
        "abstract": (
            "DPO eliminates the separate reward model in RLHF, training the policy directly "
            "on preference pairs. Simpler, more stable, and competitive with PPO-based RLHF."
        ),
        "pdf_url": "https://arxiv.org/pdf/2305.18290",
        "difficulty_tier": "pro",
        "venue": "NeurIPS 2023",
    },
    {
        "id": uid("2312.00752"),
        "arxiv_id": "2312.00752",
        "title": "Mamba: Linear-Time Sequence Modeling with Selective State Spaces",
        "authors": ["Albert Gu", "Tri Dao"],
        "abstract": (
            "Mamba proposes selective state space models (SSMs) as a Transformer alternative "
            "with linear scaling in sequence length, matching Transformers on language tasks."
        ),
        "pdf_url": "https://arxiv.org/pdf/2312.00752",
        "difficulty_tier": "pro",
        "venue": "arXiv 2023",
    },
]

# arxiv_id → list of prerequisite arxiv_ids
PREREQUISITES = {
    # Intermediate papers
    "1810.04805": ["1706.03762"],           # BERT ← Attention
    "1907.11692": ["1810.04805"],           # RoBERTa ← BERT
    "1910.10683": ["1810.04805", "1706.03762"],  # T5 ← BERT + Attention
    "2010.11929": ["1706.03762", "1512.03385"],  # ViT ← Attention + ResNet
    "2005.14165": ["1706.03762"],           # GPT-3 ← Attention
    "2001.08361": ["1706.03762"],           # Scaling Laws ← Attention
    "2103.00020": ["2010.11929"],           # CLIP ← ViT
    "2106.09685": ["1810.04805", "2005.14165"],  # LoRA ← BERT + GPT-3
    "2112.10752": ["2006.11239"],           # LDM ← DDPM
    "2204.06125": ["2103.00020", "2006.11239"],  # DALL-E 2 ← CLIP + DDPM
    # Pro papers
    "2203.02155": ["2005.14165"],           # InstructGPT ← GPT-3
    "2201.11903": ["2005.14165"],           # CoT ← GPT-3
    "2203.15556": ["2001.08361"],           # Chinchilla ← Scaling Laws
    "2205.14135": ["1706.03762"],           # FlashAttention ← Attention
    "2302.13971": ["2005.14165", "2203.15556"],  # LLaMA ← GPT-3 + Chinchilla
    "2212.08073": ["2203.02155"],           # Constitutional AI ← InstructGPT
    "2305.18290": ["2203.02155"],           # DPO ← InstructGPT
    "2312.00752": ["1706.03762"],           # Mamba ← Attention
}

# Track assignments: arxiv_id → track name
TRACK_PAPERS = {
    "beginner": [
        "1301.3781", "1412.6980", "1502.03167",
        "1512.03385", "1406.2661", "1706.03762", "2006.11239",
    ],
    "intermediate": [
        "1810.04805", "1907.11692", "1910.10683", "2010.11929",
        "2005.14165", "2001.08361", "2103.00020", "2106.09685",
        "2112.10752", "2204.06125",
    ],
    "pro": [
        "2203.02155", "2201.11903", "2203.15556", "2205.14135",
        "2302.13971", "2212.08073", "2305.18290", "2312.00752",
    ],
}


def main():
    db = SessionLocal()
    try:
        # ── Tracks ───────────────────────────────────────────────────────────
        tracks = {}
        for name in ["beginner", "intermediate", "pro"]:
            existing = db.query(Track).filter_by(domain="ML/AI", name=name).first()
            if existing:
                tracks[name] = existing
                print(f"Track '{name}' already exists, skipping.")
            else:
                track = Track(
                    id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"paperpath:track:ml-ai:{name}")),
                    domain="ML/AI",
                    name=name,
                )
                db.add(track)
                tracks[name] = track
                print(f"Created track: {name}")
        db.flush()

        # ── Papers ───────────────────────────────────────────────────────────
        paper_id_map = {}  # arxiv_id → db id
        for p in PAPERS:
            existing = db.query(Paper).filter_by(arxiv_id=p["arxiv_id"]).first()
            if existing:
                paper_id_map[p["arxiv_id"]] = existing.id
                print(f"Paper '{p['arxiv_id']}' already exists, skipping.")
                continue
            paper = Paper(
                id=p["id"],
                arxiv_id=p["arxiv_id"],
                title=p["title"],
                authors=p["authors"],
                abstract=p["abstract"],
                pdf_url=p["pdf_url"],
                difficulty_tier=p["difficulty_tier"],
                venue=p.get("venue"),
            )
            db.add(paper)
            paper_id_map[p["arxiv_id"]] = p["id"]
            print(f"Created paper: {p['arxiv_id']} — {p['title'][:50]}")
        db.flush()

        # ── Prerequisites ────────────────────────────────────────────────────
        for arxiv_id, prereq_ids in PREREQUISITES.items():
            paper_id = paper_id_map[arxiv_id]
            for prereq_arxiv_id in prereq_ids:
                prereq_id = paper_id_map[prereq_arxiv_id]
                existing = db.query(Prerequisite).filter_by(
                    paper_id=paper_id, prerequisite_paper_id=prereq_id
                ).first()
                if not existing:
                    db.add(Prerequisite(paper_id=paper_id, prerequisite_paper_id=prereq_id))
                    print(f"  Prerequisite: {arxiv_id} ← {prereq_arxiv_id}")
        db.flush()

        # ── TrackPapers ──────────────────────────────────────────────────────
        for track_name, arxiv_ids in TRACK_PAPERS.items():
            track = tracks[track_name]
            for order, arxiv_id in enumerate(arxiv_ids):
                paper_id = paper_id_map[arxiv_id]
                existing = db.query(TrackPaper).filter_by(
                    track_id=track.id, paper_id=paper_id
                ).first()
                if not existing:
                    db.add(TrackPaper(track_id=track.id, paper_id=paper_id, order_hint=order))
                    print(f"  TrackPaper: {track_name}[{order}] = {arxiv_id}")
        db.commit()
        print("\n✓ Seed complete.")

    except Exception as e:
        db.rollback()
        print(f"\n✗ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run the seed script**

```bash
cd backend
python -m scripts.seed
```

Expected output ends with:
```
✓ Seed complete.
```

- [ ] **Step 4: Verify in Supabase**

Go to Supabase → Table Editor → `papers` table. Should show 25 rows.
Go to `tracks` table. Should show 3 rows (beginner, intermediate, pro).
Go to `prerequisites` table. Should show 18 rows.
Go to `track_papers` table. Should show 25 rows.

- [ ] **Step 5: Commit**

```bash
git add backend/scripts/
git commit -m "feat: add seed script with 25 ML/AI papers, tracks, and prerequisite DAG"
git push
```

---

## Task 6: Next.js Frontend Scaffold

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/next.config.js`
- Create: `frontend/tailwind.config.ts`
- Create: `frontend/postcss.config.js`
- Create: `frontend/tsconfig.json`
- Create: `frontend/.env.local`
- Create: `frontend/app/layout.tsx`
- Create: `frontend/app/page.tsx`

- [ ] **Step 1: Scaffold Next.js app**

```bash
cd /Users/vanshdhar/Desktop/dev/my-research
npx create-next-app@14 frontend \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --no-src-dir \
  --import-alias "@/*"
```

When prompted: accept all defaults.

- [ ] **Step 2: Create frontend/.env.local (fill in your Supabase values)**

```
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

- [ ] **Step 3: Install Supabase client**

```bash
cd frontend
npm install @supabase/supabase-js @supabase/ssr
```

- [ ] **Step 4: Replace frontend/app/page.tsx with placeholder**

```tsx
export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-950 text-white">
      <h1 className="text-4xl font-bold">Paperpath</h1>
      <p className="mt-4 text-gray-400">Duolingo for research papers. Coming soon.</p>
    </main>
  );
}
```

- [ ] **Step 5: Update frontend/app/layout.tsx**

```tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Paperpath",
  description: "Duolingo for research papers",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
```

- [ ] **Step 6: Verify frontend runs**

```bash
cd frontend
npm run dev
```

Open http://localhost:3000 — should show "Paperpath / Duolingo for research papers. Coming soon." on a dark background.

Stop the server (Ctrl+C).

- [ ] **Step 7: Commit**

```bash
cd ..
git add frontend/
git commit -m "feat: scaffold Next.js 14 frontend with Tailwind dark theme"
git push
```

---

## Task 7: Update context.md + Final Brick 1 Commit

- [ ] **Step 1: Update context.md**

Replace the Brick 1 section with:

```markdown
## 2026-07-14

### Brick 1: Monorepo Scaffold + DB Schema + Seed Data ✓
- Monorepo: `frontend/` (Next.js 14) + `backend/` (FastAPI)
- DB schema: 7 tables via Alembic migration (001_initial_schema)
- Seed: 25 ML/AI papers, 3 tracks, 18 prerequisite edges, 25 track assignments
- Papers span beginner (Word2Vec → Transformers → GAN → DDPM) through
  intermediate (BERT, GPT-3, CLIP, LoRA, LDM) to pro (InstructGPT, DPO, Mamba, LLaMA)
- Frontend: Next.js 14 placeholder running on :3000
- Backend: FastAPI health endpoint running on :8000
- Next: Brick 2 — paper ingestion pipeline (arXiv fetch → PDF parse → embeddings)

### API Keys needed before Brick 2
- ANTHROPIC_API_KEY — for paper journey restructuring and quiz generation
- All Supabase keys — should be in backend/.env already
```

- [ ] **Step 2: Final commit**

```bash
git add context.md
git commit -m "docs: complete Brick 1 — scaffold, schema, seed"
git push
```

---

## Self-Review

**Spec coverage:**
- ✓ DB schema — all 7 tables from spec created
- ✓ 20–30 hand-picked papers — 25 papers seeded
- ✓ Manually drawn prerequisite edges — 18 edges seeded
- ✓ Beginner / Intermediate / Pro tracks — 3 tracks created
- ✓ Monorepo structure — frontend/ + backend/ directories
- ✓ Next.js + Tailwind — scaffold complete
- ✓ FastAPI — skeleton with health endpoint
- ✓ context.md — tracking build log

**No placeholders, no TODOs, no TBDs.**

**Type consistency:** `Paper.id`, `Track.id` are stable UUIDs generated via `uuid5` in seed — same IDs used for prerequisites and track_papers. Consistent throughout.
