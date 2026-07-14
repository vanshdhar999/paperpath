"""Claude API service for paper restructuring and quiz generation."""
import json
from anthropic import Anthropic
from app.config import settings

_client = None


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=settings.anthropic_api_key)
    return _client


def restructure_paper(title: str, abstract: str, full_text: str) -> dict:
    """Restructure a paper into a journey format using Claude.
    Returns a dict with sections: problem, prior_approaches, method, results, why_it_matters, jargon.
    """
    client = _get_client()

    # Use first 15000 chars of full text to stay within context limits
    text_excerpt = full_text[:15000] if full_text else ""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": f"""You are restructuring an academic ML/AI paper into a structured "journey" format for learners.

Paper title: {title}
Abstract: {abstract}

Full text excerpt:
{text_excerpt}

Return a JSON object with these exact keys:
{{
  "problem": "What problem does this paper address? (2-3 paragraphs, accessible to someone with basic ML knowledge)",
  "prior_approaches": "What approaches existed before this paper? What were their limitations? (2-3 paragraphs)",
  "method": "What is the paper's key contribution/method? Explain clearly. (3-4 paragraphs)",
  "results": "What were the main results and findings? Include key numbers if available. (2-3 paragraphs)",
  "why_it_matters": "Why is this paper important? What impact did it have on the field? (1-2 paragraphs)",
  "jargon": [
    {{"term": "technical term", "explanation": "simple 1-2 sentence explanation"}},
    ...list 5-10 key technical terms from the paper
  ]
}}

Return ONLY valid JSON, no markdown fences or extra text.""",
            }
        ],
    )

    text = message.content[0].text.strip()
    # Strip markdown fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    if text.startswith("json"):
        text = text[4:]

    return json.loads(text.strip())


def generate_quiz(title: str, abstract: str, journey: dict) -> list[dict]:
    """Generate a quiz from a paper's journey content.
    Returns a list of question objects.
    """
    client = _get_client()

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"""Generate a short quiz (5 questions) to test understanding of this ML/AI paper.

Paper: {title}
Abstract: {abstract}

Journey content:
Problem: {journey.get('problem', '')}
Method: {journey.get('method', '')}
Results: {journey.get('results', '')}

Return a JSON array of exactly 5 questions:
[
  {{
    "question": "The question text",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_index": 0,
    "explanation": "Why this answer is correct (1-2 sentences)"
  }},
  ...
]

Questions should test comprehension of key concepts, not memorization of numbers.
Return ONLY valid JSON array, no markdown fences or extra text.""",
            }
        ],
    )

    text = message.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    if text.startswith("json"):
        text = text[4:]

    return json.loads(text.strip())
