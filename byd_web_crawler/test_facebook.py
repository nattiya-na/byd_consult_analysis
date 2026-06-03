"""
Quick diagnostic for the Facebook mbasic crawler.
Run: .venv/bin/python test_facebook.py
"""
import sys
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

_MBASIC = "https://mbasic.facebook.com"

TARGETS = [
    ("page",  f"{_MBASIC}/BYD.Thailand"),
    ("group", f"{_MBASIC}/groups/bydthailand"),
    ("group", f"{_MBASIC}/groups/2389905174463399"),
]

HEADERS_MOBILE = {
    "User-Agent": (
        "Mozilla/5.0 (Android 14; Mobile; rv:124.0) Gecko/124.0 Firefox/124.0"
    ),
    "Accept-Language": "th-TH,th;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "DNT": "1",
}

HEADERS_DESKTOP = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "th-TH,th;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def try_fetch(label, url, headers):
    print(f"\n{'─'*60}")
    print(f"  [{label}] {url}")
    print(f"  UA: {headers['User-Agent'][:60]}...")
    try:
        r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        print(f"  Status : {r.status_code}")
        print(f"  Final URL: {r.url}")
        soup = BeautifulSoup(r.text, "lxml")
        title = soup.find("title")
        print(f"  <title>: {title.get_text(strip=True) if title else '(none)'}")

        # Detect login wall
        is_login = bool(soup.find("input", {"name": "email"}) or soup.find("form", {"id": "login_form"}))
        print(f"  Login wall: {is_login}")

        # Count articles / posts
        articles = soup.find_all("article")
        data_ft  = soup.find_all("div", attrs={"data-ft": True})
        print(f"  <article> tags: {len(articles)}")
        print(f"  div[data-ft] tags: {len(data_ft)}")

        # Show first 800 chars of body text for manual inspection
        body_text = soup.get_text(separator=" ", strip=True)[:800]
        print(f"\n  --- Body preview ---\n  {body_text}\n")

        # Show all <a> hrefs that look like post links
        post_links = [
            a["href"] for a in soup.find_all("a", href=True)
            if re.search(r"/story\.php|/posts/|/permalink/", a["href"])
        ][:5]
        print(f"  Post-like links (up to 5): {post_links}")

        return r.status_code, soup

    except requests.RequestException as exc:
        print(f"  ERROR: {exc}")
        return None, None


def main():
    session = requests.Session()

    for kind, url in TARGETS:
        # Try mobile UA first, then desktop
        for ua_label, headers in [("mobile UA", HEADERS_MOBILE), ("desktop UA", HEADERS_DESKTOP)]:
            status, soup = try_fetch(f"{kind} / {ua_label}", url, headers)
            if status == 200:
                break   # good response — no need to retry with desktop UA
            print(f"  → retrying with desktop UA...")

    print(f"\n{'='*60}")
    print("Diagnostics done.")


if __name__ == "__main__":
    main()
