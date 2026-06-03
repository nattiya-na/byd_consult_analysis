"""
Facebook crawler — mbasic.facebook.com + Playwright stealth.

Why mbasic instead of www.facebook.com:
  - Returns clean server-rendered HTML (no React, no obfuscated class names)
  - Selectors are stable across Facebook deploys
  - Still requires authentication for groups
  - Significantly less aggressive bot-detection than the full site

One-time setup (must be done before first automated run):
  1. pip install playwright-stealth
  2. Run the manual login helper:
       python -c "from crawlers.facebook_crawler import save_session_interactively; save_session_interactively()"
  3. Verify: python -c "from crawlers.facebook_crawler import check_session; check_session()"

Credentials: set FACEBOOK_EMAIL and FACEBOOK_PASSWORD in .env
"""

import asyncio
import hashlib
import json
import logging
import random
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator
from urllib.parse import urljoin

from config.keywords import FACEBOOK_GROUPS, FACEBOOK_PAGES
from config.settings import (
    FACEBOOK_EMAIL,
    FACEBOOK_MAX_POSTS,
    FACEBOOK_MIN_COMMENTS,
    FACEBOOK_PASSWORD,
)
from crawlers.base_crawler import BaseCrawler
from storage.models import PlatformEnum

logger = logging.getLogger(__name__)

_MBASIC = "https://mbasic.facebook.com"
_FB = "https://www.facebook.com"
_SESSION_DIR = Path(__file__).parent.parent / ".fb_session"
_SESSION_FILE = _SESSION_DIR / "state.json"

_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


# ---------------------------------------------------------------------------
# Public helpers for first-time setup (called from CLI / standalone)
# ---------------------------------------------------------------------------

def check_session() -> bool:
    """Return True if .fb_session/state.json has valid auth cookies."""
    if not _SESSION_FILE.exists():
        print(f"No session file at {_SESSION_FILE}")
        return False
    try:
        data = json.loads(_SESSION_FILE.read_text())
        names = {c["name"] for c in data.get("cookies", [])}
        total = len(data.get("cookies", []))
        has_auth = "c_user" in names and "xs" in names
        print(f"Session: {total} cookies, auth={'YES' if has_auth else 'NO'}")
        if not has_auth:
            print("Missing c_user/xs — session is not authenticated. Run save_session_interactively().")
        return has_auth
    except Exception as exc:
        print(f"Cannot read session: {exc}")
        return False


def save_session_interactively() -> None:
    """
    Open a visible browser so you can log in manually (handles CAPTCHA/2FA),
    then save the session. Run this ONCE before using the automated crawler.
    """
    asyncio.run(_interactive_login())


async def _interactive_login() -> None:
    try:
        from playwright.async_api import async_playwright
        from playwright_stealth import Stealth
    except ImportError:
        raise SystemExit(
            "Missing dependencies. Run:\n"
            "  pip install playwright playwright-stealth\n"
            "  playwright install chromium"
        )

    _SESSION_DIR.mkdir(exist_ok=True)
    stealth = Stealth()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        ctx = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            locale="th-TH",
            user_agent=_UA,
        )
        page = await ctx.new_page()
        await stealth.apply_stealth_async(page)
        await page.goto(_FB, wait_until="domcontentloaded")

        print("\nA browser window has opened.")
        print("1. Log in to Facebook with your account.")
        print("2. Complete any CAPTCHA or 2FA verification.")
        print("3. Once you see your Facebook homepage, come back here and press Enter.\n")
        input("Press Enter when you are logged in...")

        await ctx.storage_state(path=str(_SESSION_FILE))
        cookies = json.loads(_SESSION_FILE.read_text()).get("cookies", [])
        names = {c["name"] for c in cookies}
        if "c_user" in names and "xs" in names:
            print(f"Session saved to {_SESSION_FILE} ({len(cookies)} cookies). You can now run the automated crawler.")
        else:
            print("Warning: saved session looks incomplete (missing c_user/xs). Try again.")
        await browser.close()


# ---------------------------------------------------------------------------
# Main crawler
# ---------------------------------------------------------------------------

class FacebookCrawler(BaseCrawler):
    """
    Playwright-based scraper for BYD Facebook pages and public groups.
    Targets mbasic.facebook.com for stable HTML structure.

    Prerequisites:
        - .fb_session/state.json must contain authenticated cookies (c_user + xs)
        - Run save_session_interactively() once if session is missing or expired

    Args:
        since:  Stop collecting posts published before this datetime (UTC).
        pages:  Override FACEBOOK_PAGES from config.
        groups: Override FACEBOOK_GROUPS from config.
        headless: Set False to see the browser (useful for debugging).
    """

    def __init__(
        self,
        since: datetime | None = None,
        pages: list[str] | None = None,
        groups: list[str] | None = None,
        headless: bool = True,
    ):
        super().__init__()
        if not FACEBOOK_EMAIL or not FACEBOOK_PASSWORD:
            raise ValueError("FACEBOOK_EMAIL and FACEBOOK_PASSWORD must be set in .env")
        if not check_session():
            raise RuntimeError(
                "No valid Facebook session found.\n"
                "Run this once to log in manually:\n"
                "  from crawlers.facebook_crawler import save_session_interactively\n"
                "  save_session_interactively()"
            )
        self._since = since
        self._pages = pages if pages is not None else list(FACEBOOK_PAGES)
        self._groups = groups if groups is not None else list(FACEBOOK_GROUPS)
        self._headless = headless

    # ------------------------------------------------------------------
    # Entry point (sync wrapper over async Playwright)
    # ------------------------------------------------------------------

    def crawl(self) -> Generator[dict, None, None]:
        yield from asyncio.run(self._run())

    # ------------------------------------------------------------------
    # Async orchestration
    # ------------------------------------------------------------------

    async def _run(self) -> list[dict]:
        try:
            from playwright.async_api import async_playwright
            from playwright_stealth import Stealth
        except ImportError:
            raise SystemExit(
                "Missing dependencies. Run:\n"
                "  pip install playwright playwright-stealth\n"
                "  playwright install chromium"
            )

        results = []
        _SESSION_DIR.mkdir(exist_ok=True)
        stealth = Stealth()

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=self._headless)
            context = await browser.new_context(
                storage_state=str(_SESSION_FILE),
                viewport={"width": 1280, "height": 900},
                locale="th-TH",
                user_agent=_UA,
            )
            page = await context.new_page()
            await stealth.apply_stealth_async(page)

            try:
                # Verify session is still alive on mbasic
                await self._verify_login(page)

                for slug in self._pages:
                    url = f"{_MBASIC}/{slug}"
                    logger.info("Scraping page: %s", url)
                    posts = await self._scrape_feed(page, url, source=slug)
                    results.extend(posts)
                    await _jitter(2, 4)

                for gid in self._groups:
                    url = f"{_MBASIC}/groups/{gid}"
                    logger.info("Scraping group: %s", url)
                    posts = await self._scrape_feed(page, url, source=str(gid))
                    results.extend(posts)
                    await _jitter(2, 4)

            except SessionExpiredError:
                logger.error(
                    "Facebook session has expired. Re-run the interactive login:\n"
                    "  from crawlers.facebook_crawler import save_session_interactively\n"
                    "  save_session_interactively()"
                )
            except Exception as exc:
                logger.error("Facebook crawl failed: %s", exc, exc_info=True)
            finally:
                # Refresh saved session with any updated cookies
                await context.storage_state(path=str(_SESSION_FILE))
                await browser.close()

        return results

    # ------------------------------------------------------------------
    # Session verification
    # ------------------------------------------------------------------

    async def _verify_login(self, page) -> None:
        """Navigate to mbasic home and confirm we are logged in."""
        await page.goto(_MBASIC, wait_until="domcontentloaded")
        await _jitter(1.5, 2.5)

        # mbasic shows a login form when unauthenticated
        login_form = await page.query_selector("form#login_form, input[name='email']")
        if login_form:
            raise SessionExpiredError("mbasic.facebook.com showed a login form — session expired.")

        logger.info("Facebook session is active.")

    # ------------------------------------------------------------------
    # Feed scraping — works for both pages and groups on mbasic
    # ------------------------------------------------------------------

    async def _scrape_feed(self, page, url: str, source: str) -> list[dict]:
        await page.goto(url, wait_until="domcontentloaded")
        await _jitter(1.5, 3.0)

        bundles: list[dict] = []
        seen_ids: set[str] = set()
        current_url = url

        while len(bundles) < FACEBOOK_MAX_POSTS:
            raw_posts = await self._extract_posts_mbasic(page, source)

            stop = False
            for post in raw_posts:
                if post["post_id"] in seen_ids:
                    continue
                seen_ids.add(post["post_id"])

                pub = post.get("published_at")
                if self._since and pub and _to_utc(pub) < self._since:
                    logger.info("[%s] Reached --since cutoff.", source)
                    stop = True
                    break

                comments: list[dict] = []
                if post["comments_count"] >= FACEBOOK_MIN_COMMENTS and post.get("_post_url"):
                    await _jitter(1, 2)
                    comments = await self._fetch_comments_mbasic(page, post["_post_url"], source)

                bundles.append({
                    "post": {k: v for k, v in post.items() if not k.startswith("_")},
                    "comments": comments,
                })

                if len(bundles) >= FACEBOOK_MAX_POSTS:
                    stop = True
                    break

            if stop:
                break

            # mbasic provides a "See More" / next-page link — find and follow it
            next_url = await self._find_next_page(page, current_url)
            if not next_url:
                logger.info("[%s] No more pages.", source)
                break

            current_url = next_url
            await page.goto(current_url, wait_until="domcontentloaded")
            await _jitter(2, 3)

        logger.info("[%s] Collected %d posts.", source, len(bundles))
        return bundles

    async def _find_next_page(self, page, current_url: str) -> str | None:
        """Find the 'See More Posts' / pagination link on an mbasic feed page."""
        # mbasic paginates via a link containing cursor/timeline params
        for text in ("See More Posts", "See More Stories", "ดูเพิ่มเติม"):
            el = await page.query_selector(f"a:has-text('{text}')")
            if el:
                href = await el.get_attribute("href")
                if href:
                    return urljoin(_MBASIC, href)

        # Fallback: look for any link with pagination cursor params
        links = await page.query_selector_all("a[href*='cursor'], a[href*='timeline_cursor']")
        for link in links:
            href = await link.get_attribute("href") or ""
            if href and href != current_url:
                return urljoin(_MBASIC, href)

        return None

    # ------------------------------------------------------------------
    # Post extraction from mbasic HTML
    # ------------------------------------------------------------------

    async def _extract_posts_mbasic(self, page, source: str) -> list[dict]:
        """
        mbasic renders each post as a <div> with class 'story_body_container'.
        Structure:
          <div class="story_body_container">
            <div>  <- header with author + timestamp
            <div>  <- body text
            <div>  <- footer with like/comment/share counts + permalink
          </div>
        """
        posts = []
        # mbasic post containers
        containers = await page.query_selector_all(
            "div._4-u2._4-u8, div.story_body_container, div[data-ft]"
        )

        if not containers:
            # Fallback: try generic article-like blocks
            containers = await page.query_selector_all("div#m_story_permalink_view, section")

        for container in containers:
            try:
                p = await self._parse_mbasic_post(container, source)
                if p:
                    posts.append(p)
            except Exception as exc:
                logger.debug("[%s] Skipping container: %s", source, exc)

        return posts

    async def _parse_mbasic_post(self, container, source: str) -> dict | None:
        # ── Content ───────────────────────────────────────────────────────
        content = (await container.inner_text()).strip()
        if len(content) < 15:
            return None

        # Try to isolate just the post body (exclude header/footer noise)
        body_el = await container.query_selector("div[data-ft] p, div.story_body_container p, p")
        if body_el:
            body_text = (await body_el.inner_text()).strip()
            if len(body_text) > 10:
                content = body_text

        # ── Permalink ─────────────────────────────────────────────────────
        # mbasic post links use /story.php?story_fbid=ID or /permalink/ID
        link_el = await container.query_selector(
            "a[href*='story.php'], a[href*='/posts/'], a[href*='/permalink/']"
        )
        post_url = ""
        post_id = ""
        if link_el:
            href = (await link_el.get_attribute("href") or "").split("?")[0]
            # Reconstruct full URL
            full_href = await link_el.get_attribute("href") or ""
            post_url = urljoin(_MBASIC, full_href)
            # Extract ID from story_fbid param or /posts/ID path
            m = re.search(r"story_fbid=(\d+)|/posts/(\d+)|/permalink/(\d+)", full_href)
            if m:
                post_id = m.group(1) or m.group(2) or m.group(3) or ""

        if not post_id:
            post_id = hashlib.sha1(content[:200].encode()).hexdigest()[:20]

        # ── Timestamp ─────────────────────────────────────────────────────
        published_at = None
        # mbasic uses <abbr title="Wednesday, 1 January 2025 at 10:00"> format
        abbr_el = await container.query_selector("abbr")
        if abbr_el:
            title = await abbr_el.get_attribute("title") or ""
            published_at = _parse_fb_date(title)

        # Also check data-store JSON for utime
        if not published_at:
            data_store_el = await container.query_selector("[data-store]")
            if data_store_el:
                try:
                    ds = json.loads(await data_store_el.get_attribute("data-store") or "{}")
                    utime = ds.get("publish_time") or ds.get("creation_time")
                    if utime:
                        published_at = datetime.fromtimestamp(int(utime), tz=timezone.utc)
                except Exception:
                    pass

        # ── Reactions ─────────────────────────────────────────────────────
        reactions = 0
        # mbasic shows "X people reacted" or "Like · X" patterns
        react_el = await container.query_selector("a[href*='reaction'], a[href*='ufi/reaction']")
        if react_el:
            reactions = _parse_count(await react_el.inner_text())

        # ── Comments count ────────────────────────────────────────────────
        comments_count = 0
        # mbasic shows "X Comments" as a link
        for pattern in ("Comment", "ความคิดเห็น", "comment"):
            cmt_el = await container.query_selector(f"a[href*='comment'], a:has-text('{pattern}')")
            if cmt_el:
                comments_count = _parse_count(await cmt_el.inner_text())
                if comments_count:
                    break

        return {
            "platform": PlatformEnum.FACEBOOK,
            "post_id": post_id,
            "url": post_url,
            "title": "",
            "content": content,
            "author": source,
            "language": "th",
            "published_at": published_at,
            "likes": reactions,
            "comments_count": comments_count,
            "shares": 0,
            "raw_data": {"source": source},
            "_post_url": post_url,
        }

    # ------------------------------------------------------------------
    # Comment extraction on mbasic
    # ------------------------------------------------------------------

    async def _fetch_comments_mbasic(self, page, post_url: str, source: str) -> list[dict]:
        if not post_url:
            return []
        comments = []
        try:
            await page.goto(post_url, wait_until="domcontentloaded")
            await _jitter(1.5, 2.5)

            # mbasic comment structure: each comment is a <div> with nested text
            comment_els = await page.query_selector_all(
                "div[id^='comment_'] > div, div.comment_body, div[data-sigil='comment']"
            )

            for el in comment_els[:40]:
                text = (await el.inner_text()).strip()
                if len(text) < 5:
                    continue
                comments.append({
                    "comment_id": hashlib.sha1(text[:100].encode()).hexdigest()[:20],
                    "content": text,
                    "author": "",
                    "language": "th",
                    "published_at": None,
                    "likes": 0,
                })

            await page.go_back(wait_until="domcontentloaded")
            await _jitter(1, 2)
        except Exception as exc:
            logger.debug("[%s] Comment fetch error for %s: %s", source, post_url, exc)

        return comments


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class SessionExpiredError(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

async def _jitter(lo: float, hi: float) -> None:
    await asyncio.sleep(random.uniform(lo, hi))


def _parse_count(text: str) -> int:
    text = str(text).replace(",", "").strip()
    m = re.search(r"([\d.]+)\s*([KkMm]?)", text)
    if not m:
        return 0
    n = float(m.group(1))
    suffix = m.group(2).upper()
    if suffix == "K":
        n *= 1_000
    elif suffix == "M":
        n *= 1_000_000
    return int(n)


def _parse_fb_date(title: str) -> datetime | None:
    """Parse Facebook's human-readable date string from <abbr title="...">."""
    if not title:
        return None
    # Formats: "Wednesday, 1 January 2025 at 10:00"  or  "January 1, 2025 at 10:00 AM"
    for fmt in (
        "%A, %d %B %Y at %H:%M",
        "%B %d, %Y at %I:%M %p",
        "%d %B %Y",
        "%B %d, %Y",
    ):
        try:
            return datetime.strptime(title.strip(), fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
