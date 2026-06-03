"""
Claude-based sentiment analysis for BYD perception data.

Calls claude-haiku-4-5 via the Anthropic SDK with prompt caching on the
system prompt so repeated calls share the cached prefix and cut cost.

Output schema per text:
  overall_sentiment : positive | negative | neutral
  confidence        : 0.0 – 1.0
  aspects           : {aspect: positive | negative | neutral | not_mentioned}
  key_concerns      : [str, ...]
  key_praises       : [str, ...]
  summary           : 1-2 sentence perception summary
"""

import json
import logging
import re
import textwrap
from dataclasses import dataclass, field

import anthropic

from config.keywords import SENTIMENT_ASPECTS
from config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL, CLAUDE_MIN_TEXT_LENGTH
from storage.models import SentimentEnum

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = textwrap.dedent("""\
    You are an expert automotive market analyst specialising in EV brand \
    perception in Thailand. Analyse social-media text about BYD electric \
    vehicles and return ONLY a JSON object — no explanation, no markdown, \
    just the raw JSON.
""")

_USER_TEMPLATE = textwrap.dedent("""\
    Analyse the following Thai or English social-media text about BYD EVs.

    Text:
    \"\"\"
    {text}
    \"\"\"

    Return JSON with exactly these keys:
    {{
      "overall_sentiment": "positive" | "negative" | "neutral",
      "confidence": <float 0.0-1.0>,
      "aspects": {{
        "price": "positive" | "negative" | "neutral" | "not_mentioned",
        "range": "positive" | "negative" | "neutral" | "not_mentioned",
        "charging": "positive" | "negative" | "neutral" | "not_mentioned",
        "safety": "positive" | "negative" | "neutral" | "not_mentioned",
        "design": "positive" | "negative" | "neutral" | "not_mentioned",
        "after_sales_service": "positive" | "negative" | "neutral" | "not_mentioned",
        "reliability": "positive" | "negative" | "neutral" | "not_mentioned",
        "brand_trust": "positive" | "negative" | "neutral" | "not_mentioned"
      }},
      "key_concerns": ["<string>", ...],
      "key_praises": ["<string>", ...],
      "summary": "<1-2 sentences summarising the perception>"
    }}
""")

# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class ClaudeResult:
    sentiment: SentimentEnum
    confidence: float
    summary: str
    aspects: dict[str, str]
    key_concerns: list[str]
    key_praises: list[str]
    model_used: str
    raw_response: str


# ---------------------------------------------------------------------------
# Analyzer
# ---------------------------------------------------------------------------

_SENTIMENT_MAP = {
    "positive": SentimentEnum.POSITIVE,
    "negative": SentimentEnum.NEGATIVE,
    "neutral":  SentimentEnum.NEUTRAL,
}


class ClaudeAnalyzer:
    """Calls claude-haiku-4-5 with a prompt-cached system prompt."""

    def __init__(self):
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY must be set in .env")
        self._client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def analyze(self, text: str) -> ClaudeResult | None:
        text = text[:3000].strip()
        if not text:
            return None

        try:
            response = self._client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=700,
                system=[
                    {
                        "type": "text",
                        "text": _SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[
                    {"role": "user", "content": _USER_TEMPLATE.format(text=text)}
                ],
            )
        except anthropic.APIError as exc:
            logger.warning("Claude API error: %s", exc)
            return None

        raw = response.content[0].text if response.content else ""
        return self._parse(raw)

    def _parse(self, raw: str) -> ClaudeResult | None:
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not json_match:
            logger.warning("Claude returned no JSON: %s", raw[:200])
            return None

        try:
            data = json.loads(json_match.group())
        except json.JSONDecodeError as exc:
            logger.warning("JSON parse error: %s | raw: %s", exc, raw[:200])
            return None

        sentiment_raw = data.get("overall_sentiment", "neutral").lower()
        sentiment = _SENTIMENT_MAP.get(sentiment_raw, SentimentEnum.NEUTRAL)

        aspects = {
            asp: data.get("aspects", {}).get(asp, "not_mentioned")
            for asp in SENTIMENT_ASPECTS
        }

        return ClaudeResult(
            sentiment=sentiment,
            confidence=float(data.get("confidence", 0.5)),
            summary=data.get("summary", ""),
            aspects=aspects,
            key_concerns=data.get("key_concerns", []),
            key_praises=data.get("key_praises", []),
            model_used=CLAUDE_MODEL,
            raw_response=raw,
        )


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class SentimentPipeline:
    """Runs Claude analysis and persists results to the database."""

    def __init__(self):
        self._claude = ClaudeAnalyzer()

    def analyze_and_save(self, session, post, comment=None) -> None:
        from storage.models import SentimentResult

        target = comment if comment else post
        text = (target.content or "").strip()

        if len(text) < CLAUDE_MIN_TEXT_LENGTH:
            return

        result_data = self._claude.analyze(text)
        if result_data is None:
            return

        result = SentimentResult(
            post_id=post.id if not comment else None,
            comment_id=comment.id if comment else None,
            fast_sentiment=result_data.sentiment,
            fast_score=result_data.confidence,
            llm_sentiment=result_data.sentiment,
            llm_confidence=result_data.confidence,
            llm_summary=result_data.summary,
            aspects=result_data.aspects,
            key_concerns=result_data.key_concerns,
            key_praises=result_data.key_praises,
            llm_model_used=result_data.model_used,
            llm_raw_response=result_data.raw_response,
        )
        session.add(result)
