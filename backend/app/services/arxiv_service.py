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
