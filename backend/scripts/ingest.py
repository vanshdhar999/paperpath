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
