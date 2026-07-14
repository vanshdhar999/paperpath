import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file using PyMuPDF."""
    doc = fitz.open(pdf_path)
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    text = "\n".join(text_parts)
    # Strip NUL bytes that some PDFs produce — Postgres rejects them
    return text.replace("\x00", "")
