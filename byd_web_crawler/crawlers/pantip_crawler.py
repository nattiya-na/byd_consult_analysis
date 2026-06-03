"""
Pantip crawler — scrapes BYD-related topics from Pantip.com.

Flow:
  1. Search Pantip for each keyword → collect topic URLs + metadata
  2. Fetch each topic page → extract title, body, author, date, views, replies
  3. Extract visible reply blocks from the same page
"""

import hashlib
import logging
import re
from datetime import datetime
from typing import Generator

from bs4 import BeautifulSoup

from config.keywords import PANTIP_SEARCH_TERMS
from config.settings import PANTIP_MAX_PAGES
from crawlers.base_crawler import BaseCrawler
from storage.models import PlatformEnum

logger = logging.getLogger(__name__)

_SEARCH_URL = "https://pantip.com/search"
_BASE_URL = "https://pantip.com"


class PantipCrawler(BaseCrawler):
    """Scrapes Pantip.com for BYD-related topic posts and their replies."""

    def crawl(self) -> Generator[dict, None, None]:
        seen_topic_ids: set[str] = set()

        for term in PANTIP_SEARCH_TERMS:
            self.logger.info("Searching Pantip for: %s", term)
            for topic_url, meta in self._search(term):
                topic_id = self._extract_topic_id(topic_url)
                if not topic_id or topic_id in seen_topic_ids:
                    continue
                seen_topic_ids.add(topic_id)

                self._throttle()
                post_data, replies = self._fetch_topic(topic_url, topic_id, meta)
                if post_data:
                    yield {"post": post_data, "comments": replies}

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def _search(self, query: str) -> Generator[tuple[str, dict], None, None]:
        """Yield (topic_url, metadata_dict) from paginated search results."""
        for page in range(1, PANTIP_MAX_PAGES + 1):
            params = {
                "q": query,
                "scope": "topic",
                "order": "score",
                "page": page,
            }
            try:
                resp = self.fetch(_SEARCH_URL, params=params)
            except Exception as exc:
                self.logger.warning("Search page %d failed: %s", page, exc)
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            items = self._parse_search_results(soup)

            if not items:
                self.logger.info("No more results on page %d for '%s'", page, query)
                break

            for item in items:
                yield item

            self._throttle()

    def _parse_search_results(self, soup: BeautifulSoup) -> list[tuple[str, dict]]:
        results = []

        # Pantip search result items are <li> tags inside the results container.
        # Selectors here target the structure as of 2024-2025; adjust if Pantip redesigns.
        for item in soup.select("li.search-result-item, div.pt-list-item, article.topic-item"):
            link_tag = item.select_one("a[href*='/topic/']")
            if not link_tag:
                continue

            href = link_tag.get("href", "")
            url = href if href.startswith("http") else _BASE_URL + href

            title = link_tag.get_text(strip=True)
            views = self._parse_int(item, ".topic-views, .view-count, [data-views]")
            replies = self._parse_int(item, ".topic-replies, .reply-count, [data-replies]")

            meta = {"title": title, "views": views, "comments_count": replies}
            results.append((url, meta))

        # Fallback: look for any /topic/ links on the page
        if not results:
            for a in soup.find_all("a", href=re.compile(r"/topic/\d+")):
                href = a.get("href", "")
                url = href if href.startswith("http") else _BASE_URL + href
                meta = {"title": a.get_text(strip=True), "views": 0, "comments_count": 0}
                results.append((url, meta))

        return results

    # ------------------------------------------------------------------
    # Topic page
    # ------------------------------------------------------------------

    def _fetch_topic(self, url: str, topic_id: str, meta: dict) -> tuple[dict | None, list[dict]]:
        try:
            resp = self.fetch(url)
        except Exception as exc:
            self.logger.warning("Failed to fetch topic %s: %s", url, exc)
            return None, []

        soup = BeautifulSoup(resp.text, "html.parser")

        # --- Main post body ---
        body_tag = soup.select_one(
            "div.post-content-stored, div.main-post-story, article.post-body, div#topic-content"
        )
        content = body_tag.get_text(separator="\n", strip=True) if body_tag else ""

        if not content:
            # Broader fallback: largest text block
            candidates = [
                tag.get_text(separator="\n", strip=True)
                for tag in soup.find_all(["article", "section", "div"])
                if len(tag.get_text(strip=True)) > 100
            ]
            content = max(candidates, key=len, default="")

        if not content:
            self.logger.warning("Could not extract content from %s", url)
            return None, []

        # --- Author & date ---
        author = self._extract_text(soup, ".post-author-name, .display-name, [itemprop='author']")
        published_at = self._extract_date(soup)

        post_data = {
            "platform": PlatformEnum.PANTIP,
            "post_id": topic_id,
            "url": url,
            "title": meta.get("title", ""),
            "content": content,
            "author": author,
            "language": "th",
            "published_at": published_at,
            "views": meta.get("views", 0),
            "comments_count": meta.get("comments_count", 0),
            "raw_data": {"search_meta": meta},
        }

        replies = self._extract_replies(soup, topic_id)
        return post_data, replies

    def _extract_replies(self, soup: BeautifulSoup, topic_id: str) -> list[dict]:
        replies = []
        reply_tags = soup.select(
            "li.reply-item, div.reply-post, article.comment-item, div[data-post-type='reply']"
        )
        for idx, tag in enumerate(reply_tags):
            text_tag = tag.select_one(".reply-content, .post-content-stored, .comment-body")
            text = text_tag.get_text(separator=" ", strip=True) if text_tag else ""
            if not text:
                text = tag.get_text(separator=" ", strip=True)
            if len(text) < 5:
                continue

            author = self._extract_text(tag, ".display-name, .author-name")
            comment_id = tag.get("data-post-id") or tag.get("id") or f"{topic_id}_r{idx}"

            replies.append({
                "comment_id": str(comment_id),
                "content": text,
                "author": author,
                "language": "th",
                "likes": self._parse_int(tag, ".vote-count, .like-count"),
            })
        return replies

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_topic_id(url: str) -> str | None:
        m = re.search(r"/topic/(\d+)", url)
        return m.group(1) if m else None

    @staticmethod
    def _extract_text(soup: BeautifulSoup, selector: str) -> str:
        tag = soup.select_one(selector)
        return tag.get_text(strip=True) if tag else ""

    @staticmethod
    def _parse_int(container, selector: str) -> int:
        tag = container.select_one(selector)
        if not tag:
            return 0
        raw = re.sub(r"[^\d]", "", tag.get_text())
        return int(raw) if raw else 0

    @staticmethod
    def _extract_date(soup: BeautifulSoup) -> datetime | None:
        # Try <time datetime="..."> first
        time_tag = soup.find("time", attrs={"datetime": True})
        if time_tag:
            try:
                return datetime.fromisoformat(time_tag["datetime"].replace("Z", "+00:00"))
            except ValueError:
                pass

        # Try common date patterns in Thai text (e.g. "15 ม.ค. 2567")
        # For simplicity, return None and let it be filled later
        return None
