"""Nightly scheduler — fetches new ML/AI papers from arXiv and ingests them."""
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from app.db.session import SessionLocal
from app.db.models import Paper
from app.services.arxiv_service import fetch_arxiv_metadata
from app.services.ingestion_service import ingest_paper
import arxiv
import uuid

logger = logging.getLogger(__name__)

# arXiv categories to watch for new papers
ARXIV_CATEGORIES = ["cs.LG", "cs.AI", "cs.CL", "cs.CV"]

scheduler = BackgroundScheduler()


def fetch_recent_papers(max_results: int = 20):
    """Fetch recent ML/AI papers from arXiv and add new ones to the database."""
    db = SessionLocal()
    added = 0
    try:
        search = arxiv.Search(
            query=" OR ".join(f"cat:{cat}" for cat in ARXIV_CATEGORIES),
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )
        client = arxiv.Client()

        for result in client.results(search):
            arxiv_id = result.entry_id.split("/abs/")[-1]
            # Strip version suffix
            if "v" in arxiv_id:
                arxiv_id = arxiv_id.rsplit("v", 1)[0]

            # Skip if already in DB
            existing = db.query(Paper).filter(Paper.arxiv_id == arxiv_id).first()
            if existing:
                continue

            paper = Paper(
                id=str(uuid.uuid4()),
                arxiv_id=arxiv_id,
                title=result.title,
                authors=[a.name for a in result.authors],
                abstract=result.summary,
                pdf_url=result.pdf_url,
                published_date=result.published.date(),
                difficulty_tier="intermediate",  # default; can be reclassified later
            )
            db.add(paper)
            db.commit()

            # Run full ingestion (PDF text + embedding)
            try:
                ingest_paper(paper, db)
                added += 1
                logger.info(f"Ingested new paper: {arxiv_id} — {paper.title[:60]}")
            except Exception as e:
                logger.warning(f"Ingestion failed for {arxiv_id}: {e}")

        logger.info(f"Nightly fetch complete: {added} new papers added")
    except Exception as e:
        db.rollback()
        logger.error(f"Nightly fetch failed: {e}")
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler with nightly arXiv fetch job."""
    scheduler.add_job(
        fetch_recent_papers,
        trigger="cron",
        hour=3,
        minute=0,
        id="nightly_arxiv_fetch",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started — nightly arXiv fetch at 03:00")


def stop_scheduler():
    """Shut down the scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
