import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from config.settings import DATABASE_URL
from storage.models import Base

logger = logging.getLogger(__name__)

_engine = create_engine(
    DATABASE_URL,
    # SQLite needs this for multi-threaded access
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False,
)


@event.listens_for(_engine, "connect")
def _sqlite_pragmas(dbapi_conn, _record):
    """Enable WAL mode and foreign keys for SQLite."""
    if DATABASE_URL.startswith("sqlite"):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL")
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()


_SessionFactory = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=_engine)
    logger.info("Database schema initialized at %s", DATABASE_URL)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    session: Session = _SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def upsert_post(session: Session, post_data: dict):
    """Insert a post or skip if (platform, post_id) already exists."""
    from storage.models import Post

    existing = (
        session.query(Post)
        .filter_by(platform=post_data["platform"], post_id=post_data["post_id"])
        .first()
    )
    if existing:
        return existing, False   # (record, was_created)

    post = Post(**post_data)
    session.add(post)
    session.flush()
    return post, True


def upsert_comment(session: Session, comment_data: dict):
    """Insert a comment or skip if already exists under the same post."""
    from storage.models import Comment

    existing = (
        session.query(Comment)
        .filter_by(post_id=comment_data["post_id"], comment_id=comment_data["comment_id"])
        .first()
    )
    if existing:
        return existing, False

    comment = Comment(**comment_data)
    session.add(comment)
    session.flush()
    return comment, True


def get_crawl_state(session: Session, platform, source: str):
    """Return the CrawlState row for (platform, source), or None."""
    from storage.models import CrawlState
    return session.query(CrawlState).filter_by(platform=platform, source=source).first()


def set_crawl_state(session: Session, platform, source: str, last_crawled_at, posts_collected: int = 0):
    """Upsert the crawl state for (platform, source)."""
    from datetime import datetime
    from storage.models import CrawlState

    state = session.query(CrawlState).filter_by(platform=platform, source=source).first()
    if state:
        state.last_crawled_at = last_crawled_at
        state.posts_collected = posts_collected
        state.updated_at = datetime.utcnow()
    else:
        state = CrawlState(
            platform=platform,
            source=source,
            last_crawled_at=last_crawled_at,
            posts_collected=posts_collected,
        )
        session.add(state)
    session.flush()
    return state
