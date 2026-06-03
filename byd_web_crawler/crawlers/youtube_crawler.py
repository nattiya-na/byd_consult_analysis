"""
YouTube crawler — uses YouTube Data API v3.

Quota cost per full run (50 videos × 5 comment pages):
  search.list      : 100 units × len(SEARCH_TERMS)
  videos.list      : 1 unit × n_videos
  commentThreads   : 1 unit × pages × n_videos
  Total ≈ 1,500–3,000 units  (free quota: 10,000/day)
"""

import logging
from datetime import datetime, timezone
from typing import Generator

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config.keywords import YOUTUBE_SEARCH_TERMS
from config.settings import (
    YOUTUBE_API_KEY,
    YOUTUBE_MAX_COMMENT_PAGES,
    YOUTUBE_MAX_RESULTS,
)
from crawlers.base_crawler import BaseCrawler
from storage.models import PlatformEnum

logger = logging.getLogger(__name__)

_YT_BASE_URL = "https://www.youtube.com/watch?v="


class YouTubeCrawler(BaseCrawler):
    """Fetches BYD-related YouTube videos and their comment threads."""

    def __init__(self):
        super().__init__()
        if not YOUTUBE_API_KEY:
            raise ValueError("YOUTUBE_API_KEY is not set in .env")
        self._yt = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    # ------------------------------------------------------------------

    def crawl(self) -> Generator[dict, None, None]:
        seen_video_ids: set[str] = set()

        for query in YOUTUBE_SEARCH_TERMS:
            self.logger.info("Searching YouTube: %s", query)
            for video_id, snippet in self._search_videos(query):
                if video_id in seen_video_ids:
                    continue
                seen_video_ids.add(video_id)

                stats = self._get_video_stats(video_id)
                comments = list(self._get_comments(video_id))

                post_data = {
                    "platform": PlatformEnum.YOUTUBE,
                    "post_id": video_id,
                    "url": _YT_BASE_URL + video_id,
                    "title": snippet.get("title", ""),
                    "content": snippet.get("description", ""),
                    "author": snippet.get("channelTitle", ""),
                    "language": snippet.get("defaultAudioLanguage", "th"),
                    "published_at": self._parse_dt(snippet.get("publishedAt")),
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "comments_count": int(stats.get("commentCount", 0)),
                    "raw_data": {"snippet": snippet, "statistics": stats},
                }
                yield {"post": post_data, "comments": comments}
                self._throttle()

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def _search_videos(self, query: str) -> Generator[tuple[str, dict], None, None]:
        try:
            resp = (
                self._yt.search()
                .list(
                    q=query,
                    type="video",
                    part="id,snippet",
                    maxResults=YOUTUBE_MAX_RESULTS,
                    relevanceLanguage="th",
                    regionCode="TH",
                    order="relevance",
                )
                .execute()
            )
        except HttpError as exc:
            self.logger.error("YouTube search failed for '%s': %s", query, exc)
            return

        for item in resp.get("items", []):
            video_id = item["id"].get("videoId")
            if video_id:
                yield video_id, item["snippet"]

    # ------------------------------------------------------------------
    # Video stats
    # ------------------------------------------------------------------

    def _get_video_stats(self, video_id: str) -> dict:
        try:
            resp = (
                self._yt.videos()
                .list(part="statistics", id=video_id)
                .execute()
            )
            items = resp.get("items", [])
            return items[0]["statistics"] if items else {}
        except HttpError as exc:
            self.logger.warning("Could not fetch stats for %s: %s", video_id, exc)
            return {}

    # ------------------------------------------------------------------
    # Comments
    # ------------------------------------------------------------------

    def _get_comments(self, video_id: str) -> Generator[dict, None, None]:
        page_token = None
        page = 0

        while page < YOUTUBE_MAX_COMMENT_PAGES:
            try:
                resp = (
                    self._yt.commentThreads()
                    .list(
                        part="snippet,replies",
                        videoId=video_id,
                        maxResults=100,
                        pageToken=page_token,
                        textFormat="plainText",
                    )
                    .execute()
                )
            except HttpError as exc:
                # Comments disabled on some videos
                self.logger.debug("Comments unavailable for %s: %s", video_id, exc)
                break

            for thread in resp.get("items", []):
                top = thread["snippet"]["topLevelComment"]["snippet"]
                yield {
                    "comment_id": thread["id"],
                    "content": top.get("textDisplay", ""),
                    "author": top.get("authorDisplayName", ""),
                    "language": "th",
                    "published_at": self._parse_dt(top.get("publishedAt")),
                    "likes": int(top.get("likeCount", 0)),
                }

                # Include direct replies
                for reply in thread.get("replies", {}).get("comments", []):
                    rs = reply["snippet"]
                    yield {
                        "comment_id": reply["id"],
                        "content": rs.get("textDisplay", ""),
                        "author": rs.get("authorDisplayName", ""),
                        "language": "th",
                        "published_at": self._parse_dt(rs.get("publishedAt")),
                        "likes": int(rs.get("likeCount", 0)),
                    }

            page_token = resp.get("nextPageToken")
            if not page_token:
                break
            page += 1
            self._throttle(extra=0.5)

    # ------------------------------------------------------------------

    @staticmethod
    def _parse_dt(iso_str: str | None) -> datetime | None:
        if not iso_str:
            return None
        try:
            return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        except ValueError:
            return None
