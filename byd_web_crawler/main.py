"""
BYD Perception Crawler — CLI entry point.

Commands:
  crawl pantip     Scrape Pantip.com
  crawl youtube    Scrape YouTube via Data API v3
  crawl twitter    Scrape Twitter/X via API v2
  crawl facebook   Scrape Facebook via Playwright
  crawl all        Run all four crawlers sequentially

  analyze fast     Run fast classifier on un-analyzed records
  analyze deep     Run fast + LLM deep analysis on un-analyzed records
  analyze topics   Fit BERTopic on all posts
  analyze viz      Generate HTML dashboards + word clouds
"""

import logging
import sys
from datetime import datetime, timezone

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn

from storage.database import get_session, init_db, upsert_comment, upsert_post

console = Console()

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)
logger = logging.getLogger("main")


# ---------------------------------------------------------------------------
# CLI root
# ---------------------------------------------------------------------------

@click.group()
def cli():
    """BYD Perception Web Crawler & Analyser."""
    init_db()


# ---------------------------------------------------------------------------
# crawl commands
# ---------------------------------------------------------------------------

@cli.group()
def crawl():
    """Crawl social media platforms for BYD-related content."""


@crawl.command("pantip")
def crawl_pantip():
    """Scrape Pantip.com."""
    from crawlers.pantip_crawler import PantipCrawler
    _run_crawler(PantipCrawler(), "Pantip")


@crawl.command("youtube")
def crawl_youtube():
    """Fetch BYD videos + comments via YouTube Data API v3."""
    from crawlers.youtube_crawler import YouTubeCrawler
    _run_crawler(YouTubeCrawler(), "YouTube")


@crawl.command("twitter")
def crawl_twitter():
    """Search BYD tweets via Twitter API v2."""
    from crawlers.twitter_crawler import TwitterCrawler
    _run_crawler(TwitterCrawler(), "Twitter/X")


@crawl.command("facebook")
@click.option("--pages", default=None, help="Comma-separated page slugs (overrides config)")
@click.option("--groups", default=None, help="Comma-separated group IDs/slugs (overrides config)")
@click.option("--since", default=None, metavar="YYYY-MM-DD", help="Skip posts older than this date")
@click.option("--no-headless", is_flag=True, default=False, help="Show browser window (useful for debugging)")
@click.option("--setup", is_flag=True, default=False, help="Run interactive login to save session (do this once)")
def crawl_facebook(pages, groups, since, no_headless, setup):
    """Scrape BYD Facebook pages and groups via mbasic.facebook.com."""
    from crawlers.facebook_crawler import FacebookCrawler, save_session_interactively, check_session

    if setup:
        save_session_interactively()
        return

    if not check_session():
        console.print(
            "[red]No valid Facebook session.[/] Run setup first:\n"
            "  python main.py crawl facebook --setup"
        )
        sys.exit(1)

    since_dt = None
    if since:
        try:
            since_dt = datetime.fromisoformat(since).replace(tzinfo=timezone.utc)
        except ValueError:
            console.print(f"[red]Invalid --since date:[/] {since!r}. Use YYYY-MM-DD format.")
            sys.exit(1)

    pages_list = [p.strip() for p in pages.split(",")] if pages else None
    groups_list = [g.strip() for g in groups.split(",")] if groups else None
    headless = not no_headless

    _run_crawler(
        FacebookCrawler(since=since_dt, pages=pages_list, groups=groups_list, headless=headless),
        "Facebook",
    )


@crawl.command("all")
@click.option("--since", default=None, metavar="YYYY-MM-DD", help="Skip posts older than this date")
def crawl_all(since):
    """Run Facebook and YouTube crawlers sequentially."""
    from crawlers.facebook_crawler import FacebookCrawler
    from crawlers.youtube_crawler import YouTubeCrawler

    since_dt = None
    if since:
        try:
            since_dt = datetime.fromisoformat(since).replace(tzinfo=timezone.utc)
        except ValueError:
            console.print(f"[red]Invalid --since date:[/] {since!r}. Use YYYY-MM-DD format.")
            sys.exit(1)

    try:
        _run_crawler(FacebookCrawler(since=since_dt), "Facebook")
    except Exception as exc:
        logger.error("Facebook crawler failed: %s", exc)

    try:
        _run_crawler(YouTubeCrawler(), "YouTube")
    except Exception as exc:
        logger.error("YouTube crawler failed: %s", exc)


def _run_crawler(crawler, name: str) -> None:
    console.rule(f"[bold blue]{name} Crawler")
    posts_saved = comments_saved = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Crawling {name}...", total=None)

        with get_session() as session:
            for bundle in crawler.crawl():
                post_data = {**bundle["post"], "crawled_at": datetime.utcnow()}
                post, created = upsert_post(session, post_data)
                if created:
                    posts_saved += 1

                for c in bundle.get("comments", []):
                    c_data = {**c, "post_id": post.id}
                    _, c_created = upsert_comment(session, c_data)
                    if c_created:
                        comments_saved += 1

                progress.update(task, description=f"{name}: {posts_saved} posts, {comments_saved} comments")

    console.print(f"[green]Done:[/] {posts_saved} new posts, {comments_saved} new comments saved.")


# ---------------------------------------------------------------------------
# analyze commands
# ---------------------------------------------------------------------------

@cli.group()
def analyze():
    """Run sentiment analysis, topic modeling, or visualization."""


@analyze.command("fast")
@click.option("--limit", default=0, help="Max records to process (0=all)")
def analyze_fast(limit):
    """Fast classifier only — no LLM, runs on CPU."""
    _run_sentiment(run_llm=False, limit=limit)


@analyze.command("deep")
@click.option("--limit", default=0, help="Max records to process (0=all)")
def analyze_deep(limit):
    """Fast classifier + LLM deep analysis (requires HF_API_TOKEN or local GPU)."""
    _run_sentiment(run_llm=True, limit=limit)


def _run_sentiment(run_llm: bool, limit: int) -> None:
    from analysis.sentiment import SentimentPipeline
    from storage.models import Post, SentimentResult

    console.rule("[bold blue]Sentiment Analysis")
    pipeline = SentimentPipeline(run_llm=run_llm)
    processed = 0

    with get_session() as session:
        query = (
            session.query(Post)
            .outerjoin(SentimentResult, SentimentResult.post_id == Post.id)
            .filter(SentimentResult.id.is_(None))
        )
        if limit:
            query = query.limit(limit)

        posts = query.all()
        console.print(f"Analyzing {len(posts)} un-processed posts...")

        with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as prog:
            task = prog.add_task("Analyzing...", total=len(posts))
            for post in posts:
                pipeline.analyze_and_save(session, post)
                processed += 1
                prog.update(task, advance=1, description=f"Analyzed {processed}/{len(posts)}")

    console.print(f"[green]Done:[/] {processed} posts analyzed.")


@analyze.command("topics")
@click.option("--n-topics", default=10, help="Number of topics")
@click.option("--save", default="models/topic_model", help="Path to save fitted model")
def analyze_topics(n_topics, save):
    """Fit BERTopic on all crawled posts."""
    from analysis.topic_modeling import TopicModeler
    from storage.models import Post

    console.rule("[bold blue]Topic Modeling")
    with get_session() as session:
        modeler = TopicModeler(n_topics=n_topics)
        topics, probs, info = modeler.run_from_db(session)
        modeler.save(save)

    console.print(info.to_string())
    console.print(f"[green]Model saved →[/] {save}")


@analyze.command("viz")
@click.option("--output", default="outputs", help="Output directory for HTML charts")
def analyze_viz(output):
    """Generate Plotly dashboards and word cloud PNGs."""
    from analysis.visualization import build_dashboard

    console.rule("[bold blue]Visualization")
    with get_session() as session:
        build_dashboard(session, output_dir=output)
    console.print(f"[green]Dashboard written →[/] {output}/")


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cli()
