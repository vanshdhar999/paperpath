"""LLM service for paper restructuring and quiz generation using Groq (free tier)."""
import json
from groq import Groq
from app.config import settings

_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=settings.groq_api_key)
    return _client


def _parse_json(text: str):
    """Strip markdown fences and parse JSON."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    if text.startswith("json"):
        text = text[4:]
    return json.loads(text.strip())


def restructure_paper(title: str, abstract: str, full_text: str) -> dict:
    """Restructure a paper into a journey format.
    Returns a dict with sections: problem, prior_approaches, method, results, why_it_matters, jargon.
    """
    client = _get_client()

    # Groq has smaller context than Claude — use first 8000 chars
    text_excerpt = full_text[:8000] if full_text else ""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an expert ML/AI researcher who explains papers clearly to learners. Always return valid JSON only, no markdown fences.",
            },
            {
                "role": "user",
                "content": f"""Restructure this ML/AI paper into a structured "journey" format for learners.

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

Return ONLY valid JSON.""",
            },
        ],
        temperature=0.3,
        max_tokens=4000,
        response_format={"type": "json_object"},
    )

    return _parse_json(response.choices[0].message.content)


def generate_quiz(title: str, abstract: str, journey: dict) -> list[dict]:
    """Generate a quiz from a paper's journey content.
    Returns a list of question objects.
    """
    client = _get_client()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a quiz generator for ML/AI papers. Always return valid JSON only.",
            },
            {
                "role": "user",
                "content": f"""Generate a short quiz (5 questions) to test understanding of this ML/AI paper.

Paper: {title}
Abstract: {abstract}

Journey content:
Problem: {journey.get('problem', '')}
Method: {journey.get('method', '')}
Results: {journey.get('results', '')}

Return a JSON object with a "questions" key containing an array of exactly 5 questions:
{{
  "questions": [
    {{
      "question": "The question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_index": 0,
      "explanation": "Why this answer is correct (1-2 sentences)"
    }}
  ]
}}

Questions should test comprehension of key concepts, not memorization of numbers.
Return ONLY valid JSON.""",
            },
        ],
        temperature=0.3,
        max_tokens=2000,
        response_format={"type": "json_object"},
    )

    result = _parse_json(response.choices[0].message.content)
    # Handle both direct array and wrapped {"questions": [...]} format
    if isinstance(result, list):
        return result
    return result.get("questions", result)
