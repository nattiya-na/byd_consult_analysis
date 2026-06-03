"""
Twitter / X crawler — uses Twitter API v2 via Tweepy.

Free tier: search_recent_tweets, last 7 days, 1 request/15 min.
Basic tier ($100/month): higher rate limits, 30-day history.

The crawler respects rate-limit headers automatically via Tweepy's wait_on_rate_limit.
"""

import logging
from datetime import datetime, timezone
from typing import Generator

import tweepy

from config.keywords import TWITTER_QUERIES
from config.settings import (
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_BEARER_TOKEN,
    TWITTER_MAX_RESULTS,
)
from crawlers.base_crawler import BaseCrawler
from storage.models import PlatformEnum

logger = logging.getLogger(__name__)

_TWEET_FIELDS = ["created_at", "author_id", "public_metrics", "lang", "conversation_id"]
_EXPANSIONS = ["author_id"]
_USER_FIELDS = ["name", "username"]


class TwitterCrawler(BaseCrawler):
    """Searches recent tweets mentioning BYD and yields structured post dicts."""

    def __init__(self):
        super().__init__()
        if not TWITTER_BEARER_TOKEN:
            raise ValueError("TWITTER_BEARER_TOKEN is not set in .env")
        self._client = tweepy.Client(
            bearer_token=TWITTER_BEARER_TOKEN,
            consumer_key=TWITTER_API_KEY or None,
            consumer_secret=TWITTER_API_SECRET or None,
            access_token=TWITTER_ACCESS_TOKEN or None,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET or None,
            wait_on_rate_limit=True,
        )

    # ------------------------------------------------------------------

    def crawl(self) -> Generator[dict, None, None]:
        seen_tweet_ids: set[str] = set()

        for query in TWITTER_QUERIES:
            self.logger.info("Twitter search: %s", query)
            for tweet_data in self._search(query):
                tweet_id = tweet_data["post_id"]
                if tweet_id in seen_tweet_ids:
                    continue
                seen_tweet_ids.add(tweet_id)
                # Twitter replies are separate tweets; we surface them as posts.
                # For true thread structure, a separate conversation fetch would be needed.
                yield {"post": tweet_data, "comments": []}

    # ------------------------------------------------------------------

    def _search(self, query: str) -> Generator[dict, None, None]:
        paginator = tweepy.Paginator(
            self._client.search_recent_tweets,
            query=query,
            max_results=min(TWITTER_MAX_RESULTS, 100),  # API max per page is 100
            tweet_fields=_TWEET_FIELDS,
            expansions=_EXPANSIONS,
            user_fields=_USER_FIELDS,
        )

        users: dict[str, str] = {}

        try:
            for response in paginator:
                if response.includes and "users" in response.includes:
                    users = {u.id: u.username for u in response.includes["users"]}

                for tweet in (response.data or []):
                    metrics = tweet.public_metrics or {}
                    author_name = users.get(tweet.author_id, str(tweet.author_id))

                    yield {
                        "platform": PlatformEnum.TWITTER,
                        "post_id": str(tweet.id),
                        "url": f"https://twitter.com/i/web/status/{tweet.id}",
                        "title": "",
                        "content": tweet.text,
                        "author": author_name,
                        "language": tweet.lang or "th",
                        "published_at": tweet.created_at,
                        "likes": metrics.get("like_count", 0),
                        "comments_count": metrics.get("reply_count", 0),
                        "shares": metrics.get("retweet_count", 0),
                        "views": metrics.get("impression_count", 0),
                        "raw_data": {
                            "public_metrics": metrics,
                            "conversation_id": str(tweet.conversation_id or ""),
                        },
                    }
        except tweepy.TweepyException as exc:
            self.logger.error("Twitter search error for query '%s': %s", query, exc)
