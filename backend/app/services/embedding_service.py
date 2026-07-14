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
    truncated = text[:2000]
    embedding = model.encode(truncated)
    return embedding.tolist()
