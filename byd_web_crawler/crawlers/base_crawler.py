import logging
import random
import time
from abc import ABC, abstractmethod
from typing import Generator

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import MAX_RETRIES, REQUEST_DELAY

logger = logging.getLogger(__name__)

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]


class BaseCrawler(ABC):
    """Abstract base: managed HTTP session, rate-limiting, retry logic."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = self._build_session()

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=MAX_RETRIES,
            backoff_factor=1.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _headers(self, extra: dict | None = None) -> dict:
        h = {
            "User-Agent": random.choice(_USER_AGENTS),
            "Accept-Language": "th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        if extra:
            h.update(extra)
        return h

    def _throttle(self, extra: float = 0.0) -> None:
        """Sleep REQUEST_DELAY ± random jitter to avoid rate-limiting."""
        delay = REQUEST_DELAY + random.uniform(0.0, 1.5) + extra
        self.logger.debug("Throttling %.2fs", delay)
        time.sleep(delay)

    def fetch(self, url: str, params: dict | None = None, **kwargs) -> requests.Response:
        kwargs.setdefault("headers", self._headers())
        kwargs.setdefault("timeout", 30)
        response = self.session.get(url, params=params, **kwargs)
        response.raise_for_status()
        return response

    # ------------------------------------------------------------------
    # Subclass contract
    # ------------------------------------------------------------------

    @abstractmethod
    def crawl(self) -> Generator[dict, None, None]:
        """Yield raw post dicts ready to be stored in the DB.

        Each dict must contain at minimum:
            platform, post_id, content, crawled_at
        """
        ...
