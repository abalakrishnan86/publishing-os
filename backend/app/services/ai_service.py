import json
import logging

import anthropic

from app.config import ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
MODEL = "claude-sonnet-4-6"
MAX_CHARS = 60_000


def _truncate(text: str) -> str:
    if len(text) <= MAX_CHARS:
        return text
    # Keep first 50k + last 10k chars with a separator note
    return (
        text[:50_000]
        + "\n\n[... manuscript truncated for analysis ...]\n\n"
        + text[-10_000:]
    )


def _call(system: str, user: str) -> dict:
    response = _client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    raw = response.content[0].text
    # Strip markdown code fences if present
    if raw.strip().startswith("```"):
        raw = raw.strip().lstrip("`").lstrip("json").strip().rstrip("`").strip()
    return json.loads(raw)


def analyze_manuscript(text: str) -> dict:
    excerpt = _truncate(text)
    system = (
        "You are a professional literary analyst and publishing consultant. "
        "Analyze manuscripts and return structured JSON assessments. "
        "Be specific, actionable, and base your analysis strictly on the provided text. "
        "Respond with a single valid JSON object and nothing else."
    )
    user = f"""Analyze this manuscript.

MANUSCRIPT TEXT:
{excerpt}

Return a JSON object with exactly these keys:
- genre: string (primary genre)
- themes: array of strings (3-7 major themes)
- writing_style: string (detailed description of style, voice, and tone)
- target_audience: string (age range, interests, demographics)
- readability_score: string (e.g. "Grade 8 / General Adult")
- strengths: array of strings (3-5 specific strengths)
- weaknesses: array of strings (3-5 areas for improvement)"""
    return _call(system, user)


def generate_metadata(text: str) -> dict:
    excerpt = _truncate(text)
    system = (
        "You are a professional book editor and publishing metadata specialist. "
        "Generate publishing-ready metadata that maximizes discoverability and reader appeal. "
        "All suggestions must be grounded in the provided manuscript content. "
        "Respond with a single valid JSON object and nothing else."
    )
    user = f"""Generate publishing metadata for this manuscript.

MANUSCRIPT EXCERPT:
{excerpt}

Return a JSON object with exactly these keys:
- title_suggestions: array of 5 compelling, market-oriented title strings
- subtitle: string (one subtitle that complements the title suggestions)
- description: string (250-300 word back-matter description)
- keywords: array of 10-15 search keywords/phrases
- bisac_categories: array of 2-3 strings, each formatted as "CODE — Description"
- author_bio_prompt: string (a template the author can fill in for their bio)"""
    return _call(system, user)


def generate_marketing(text: str, title: str) -> dict:
    excerpt = _truncate(text)
    system = (
        "You are a book marketing expert and copywriter specializing in publishing. "
        "Create compelling, platform-appropriate marketing materials that drive engagement and sales. "
        "All copy must be authentic to the manuscript's voice and content. "
        "Respond with a single valid JSON object and nothing else."
    )
    user = f"""Create marketing materials for this manuscript.

BOOK TITLE: {title}

MANUSCRIPT EXCERPT:
{excerpt}

Return a JSON object with exactly these keys:
- back_cover_blurb: string (150-200 words, hook + premise + stakes, no spoilers)
- amazon_description: string (400-500 words, SEO-optimized, includes genre keywords)
- twitter_post: string (max 280 chars, includes relevant hashtags)
- linkedin_post: string (150-200 words, professional/thought-leadership angle)
- instagram_post: string (150 words followed by a newline and 5-10 hashtags)
- press_release_excerpt: string (200-250 words, AP style, 3rd person)
- elevator_pitch: string (2-3 sentences, max 60 words)"""
    return _call(system, user)
