# Brick 2: Paper Ingestion Pipeline

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a pipeline that takes an arXiv ID, fetches metadata from arXiv API, downloads the PDF, extracts text via PyMuPDF, generates a 384-dim embedding via sentence-transformers, and updates the paper row in the DB. Run this pipeline on all 25 seeded papers.

**Architecture:** Three service modules in `backend/app/services/`: arxiv client, PDF extractor, embedding generator. An orchestrator `ingestion_service` ties them together. A management command `scripts/ingest.py` runs the pipeline on all papers missing `full_text` or `embedding`.

**Tech Stack:** arxiv Python package, PyMuPDF (fitz), sentence-transformers (all-MiniLM-L6-v2), SQLAlchemy

## Global Constraints

- Python 3.11+ via backend/.venv
- All DB access via SQLAlchemy models from app.db.models
- Embeddings: all-MiniLM-L6-v2 (384 dimensions, matching Vector(384) column)
- PDF storage: download to a temp file, extract text, delete temp file (no persistent PDF storage in v1)
- Pipeline must be idempotent: skip papers that already have full_text AND embedding
- Run all commands from backend/ directory using .venv/bin/python

---

## Task 1: arXiv Metadata + PDF Fetch Service

**Files:**
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/arxiv_service.py`

**Produces:**
- `fetch_arxiv_metadata(arxiv_id: str) -> dict` — returns {title, authors, abstract, published_date, pdf_url}
- `download_pdf(pdf_url: str) -> str` — downloads PDF to temp file, returns file path

- [ ] **Step 1: Create backend/app/services/__init__.py**

Empty file.

- [ ] **Step 2: Create backend/app/services/arxiv_service.py**

```python
import arxiv
import tempfile
import httpx
import os


def fetch_arxiv_metadata(arxiv_id: str) -> dict:
    """Fetch paper metadata from arXiv API."""
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    results = list(client.results(search))
    if not results:
        raise ValueError(f"No arXiv paper found for ID: {arxiv_id}")
    paper = results[0]
    return {
        "title": paper.title,
        "authors": [a.name for a in paper.authors],
        "abstract": paper.summary,
        "published_date": paper.published.date(),
        "pdf_url": paper.pdf_url,
    }


def download_pdf(pdf_url: str) -> str:
    """Download PDF to a temp file, return the file path."""
    response = httpx.get(pdf_url, follow_redirects=True, timeout=60.0)
    response.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.write(response.content)
    tmp.close()
    return tmp.name
```

- [ ] **Step 3: Verify import**

```bash
cd backend && .venv/bin/python -c "from app.services.arxiv_service import fetch_arxiv_metadata, download_pdf; print('OK')"
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/
git commit -m "feat: add arXiv metadata fetch and PDF download service"
git push
```

---

## Task 2: PDF Text Extraction Service

**Files:**
- Create: `backend/app/services/pdf_service.py`

**Produces:**
- `extract_text_from_pdf(pdf_path: str) -> str` — extracts all text from a PDF file using PyMuPDF

- [ ] **Step 1: Create backend/app/services/pdf_service.py**

```python
import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file using PyMuPDF."""
    doc = fitz.open(pdf_path)
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n".join(text_parts)
```

- [ ] **Step 2: Verify import**

```bash
.venv/bin/python -c "from app.services.pdf_service import extract_text_from_pdf; print('OK')"
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/pdf_service.py
git commit -m "feat: add PDF text extraction service via PyMuPDF"
git push
```

---

## Task 3: Embedding Generation Service

**Files:**
- Create: `backend/app/services/embedding_service.py`

**Produces:**
- `generate_embedding(text: str) -> list[float]` — returns a 384-dim embedding vector
- Model loaded lazily on first call (singleton pattern)

- [ ] **Step 1: Create backend/app/services/embedding_service.py**

```python
from sentence_transformers import SentenceTransformer

_model = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def generate_embedding(text: str) -> list[float]:
    """Generate a 384-dim embedding for the given text.
    Uses the abstract/title as input (not full paper text) for better semantic matching.
    """
    model = _get_model()
    # Truncate to ~512 tokens worth of text (model max is 256 word pieces)
    truncated = text[:2000]
    embedding = model.encode(truncated)
    return embedding.tolist()
```

- [ ] **Step 2: Verify embedding generation works**

```bash
.venv/bin/python -c "
from app.services.embedding_service import generate_embedding
vec = generate_embedding('Attention is all you need. A transformer architecture.')
print(f'Embedding dim: {len(vec)}')
assert len(vec) == 384, f'Expected 384, got {len(vec)}'
print('OK')
"
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/embedding_service.py
git commit -m "feat: add sentence-transformer embedding service (all-MiniLM-L6-v2)"
git push
```

---

## Task 4: Ingestion Orchestrator + CLI Script

**Files:**
- Create: `backend/app/services/ingestion_service.py`
- Create: `backend/scripts/ingest.py`

**Consumes:**
- `app.services.arxiv_service.fetch_arxiv_metadata`, `download_pdf`
- `app.services.pdf_service.extract_text_from_pdf`
- `app.services.embedding_service.generate_embedding`
- `app.db.session.SessionLocal`
- `app.db.models.Paper`

- [ ] **Step 1: Create backend/app/services/ingestion_service.py**

```python
import os
from app.services.arxiv_service import fetch_arxiv_metadata, download_pdf
from app.services.pdf_service import extract_text_from_pdf
from app.services.embedding_service import generate_embedding
from app.db.session import SessionLocal
from app.db.models import Paper


def ingest_paper(paper: Paper, db) -> bool:
    """Run the full ingestion pipeline for a single paper.
    Returns True if the paper was updated, False if skipped.
    """
    if paper.full_text and paper.embedding:
        return False

    print(f"  Ingesting: {paper.arxiv_id} — {paper.title[:60]}")

    # Step 1: Fetch metadata from arXiv (update any missing fields)
    try:
        meta = fetch_arxiv_metadata(paper.arxiv_id)
        if not paper.abstract:
            paper.abstract = meta["abstract"]
        if not paper.authors or len(paper.authors) == 0:
            paper.authors = meta["authors"]
        if not paper.published_date:
            paper.published_date = meta["published_date"]
        if not paper.pdf_url:
            paper.pdf_url = meta["pdf_url"]
    except Exception as e:
        print(f"    Warning: arXiv metadata fetch failed: {e}")

    # Step 2: Download PDF and extract text
    if not paper.full_text:
        try:
            pdf_url = paper.pdf_url or f"https://arxiv.org/pdf/{paper.arxiv_id}"
            pdf_path = download_pdf(pdf_url)
            paper.full_text = extract_text_from_pdf(pdf_path)
            os.unlink(pdf_path)
            print(f"    Extracted {len(paper.full_text)} chars of text")
        except Exception as e:
            print(f"    Warning: PDF extraction failed: {e}")

    # Step 3: Generate embedding from abstract (or title as fallback)
    if not paper.embedding:
        try:
            embed_text = paper.abstract or paper.title
            paper.embedding = generate_embedding(embed_text)
            print(f"    Generated 384-dim embedding")
        except Exception as e:
            print(f"    Warning: Embedding generation failed: {e}")

    db.commit()
    return True


def ingest_all_papers():
    """Run ingestion on all papers missing full_text or embedding."""
    db = SessionLocal()
    try:
        papers = db.query(Paper).all()
        total = len(papers)
        ingested = 0
        skipped = 0

        print(f"Found {total} papers in database")
        for paper in papers:
            if ingest_paper(paper, db):
                ingested += 1
            else:
                skipped += 1

        print(f"\nDone: {ingested} ingested, {skipped} skipped (already complete)")
    except Exception as e:
        db.rollback()
        print(f"Ingestion failed: {e}")
        raise
    finally:
        db.close()
```

- [ ] **Step 2: Create backend/scripts/ingest.py**

```python
"""
Run paper ingestion pipeline on all papers missing full_text or embedding.
Usage: cd backend && .venv/bin/python -m scripts.ingest
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.services.ingestion_service import ingest_all_papers

if __name__ == "__main__":
    print("Starting paper ingestion pipeline...")
    ingest_all_papers()
```

- [ ] **Step 3: Run ingestion on all 25 papers**

```bash
cd backend && .venv/bin/python -m scripts.ingest
```

Expected: processes all 25 papers, extracts text, generates embeddings.

- [ ] **Step 4: Verify data in DB**

```bash
.venv/bin/python -c "
from dotenv import load_dotenv; load_dotenv()
from app.db.session import SessionLocal
from app.db.models import Paper
db = SessionLocal()
total = db.query(Paper).count()
with_text = db.query(Paper).filter(Paper.full_text.isnot(None)).count()
with_embed = db.query(Paper).filter(Paper.embedding.isnot(None)).count()
print(f'Total: {total}, With text: {with_text}, With embedding: {with_embed}')
db.close()
"
```

Expected: `Total: 25, With text: 25, With embedding: 25`

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/ingestion_service.py backend/scripts/ingest.py
git commit -m "feat: add paper ingestion pipeline — arXiv fetch, PDF parse, embeddings"
git push
```

---

## Task 5: Update context.md for Brick 2

- [ ] **Step 1: Update context.md**

Add after the Brick 1 section:

```markdown
### Brick 2: Paper Ingestion Pipeline ✓
- Pipeline: arXiv API → PDF download → PyMuPDF text extraction → sentence-transformer embeddings
- Services: arxiv_service, pdf_service, embedding_service, ingestion_service
- All 25 papers ingested with full_text and 384-dim embeddings
- CLI: `cd backend && .venv/bin/python -m scripts.ingest`
- Next: Brick 3 — Auth (Supabase magic link) + dashboard shell
```

- [ ] **Step 2: Commit**

```bash
git add context.md
git commit -m "docs: complete Brick 2 — paper ingestion pipeline"
git push
```
