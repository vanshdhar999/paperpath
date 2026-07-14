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
    if paper.full_text and paper.embedding is not None:
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
