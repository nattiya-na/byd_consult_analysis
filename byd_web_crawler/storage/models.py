import enum
from datetime import datetime

from sqlalchemy import (
    JSON, Column, DateTime, Enum, Float,
    ForeignKey, Integer, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class PlatformEnum(str, enum.Enum):
    FACEBOOK = "facebook"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    PANTIP = "pantip"


class SentimentEnum(str, enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class Post(Base):
    __tablename__ = "posts"
    __table_args__ = (
        UniqueConstraint("platform", "post_id", name="uq_post_platform_id"),
    )

    id = Column(Integer, primary_key=True)
    platform = Column(Enum(PlatformEnum), nullable=False, index=True)
    post_id = Column(String(255), nullable=False)      # platform-native ID / URL hash
    url = Column(Text)
    title = Column(Text)                               # used by YouTube / Pantip
    content = Column(Text, nullable=False)
    author = Column(String(255))
    language = Column(String(10))                      # "th" | "en" | "unknown"
    published_at = Column(DateTime, index=True)
    crawled_at = Column(DateTime, default=datetime.utcnow)

    # Engagement metrics (best-effort; 0 if unavailable)
    likes = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    views = Column(Integer, default=0)

    raw_data = Column(JSON)   # original API payload / scraped dict

    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    sentiment = relationship(
        "SentimentResult", back_populates="post",
        uselist=False, cascade="all, delete-orphan",
        foreign_keys="SentimentResult.post_id",
    )

    def __repr__(self):
        return f"<Post platform={self.platform} id={self.post_id}>"


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (
        UniqueConstraint("post_id", "comment_id", name="uq_comment_post_native"),
    )

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    comment_id = Column(String(255))               # platform-native ID
    content = Column(Text, nullable=False)
    author = Column(String(255))
    language = Column(String(10))
    published_at = Column(DateTime)
    likes = Column(Integer, default=0)

    post = relationship("Post", back_populates="comments")
    sentiment = relationship(
        "SentimentResult", back_populates="comment",
        uselist=False, cascade="all, delete-orphan",
        foreign_keys="SentimentResult.comment_id",
    )

    def __repr__(self):
        return f"<Comment id={self.comment_id} post={self.post_id}>"


class SentimentResult(Base):
    """Stores both the fast-classifier result and the deep LLM analysis."""

    __tablename__ = "sentiment_results"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True, unique=True)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True, unique=True)

    # --- Fast classifier (XLM-RoBERTa) ---
    fast_sentiment = Column(Enum(SentimentEnum))
    fast_score = Column(Float)                    # confidence 0–1

    # --- Deep LLM analysis ---
    llm_sentiment = Column(Enum(SentimentEnum))
    llm_confidence = Column(Float)
    llm_summary = Column(Text)                    # 1-2 sentence perception summary
    aspects = Column(JSON)                         # {price: "positive", range: "neutral", ...}
    key_concerns = Column(JSON)                    # ["long charge time", ...]
    key_praises = Column(JSON)                     # ["sleek design", ...]
    llm_model_used = Column(String(100))
    llm_raw_response = Column(Text)               # raw LLM output for debugging

    analyzed_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="sentiment", foreign_keys=[post_id])
    comment = relationship("Comment", back_populates="sentiment", foreign_keys=[comment_id])

    def __repr__(self):
        return f"<SentimentResult fast={self.fast_sentiment} llm={self.llm_sentiment}>"


class CrawlState(Base):
    """Tracks the last successful crawl per (platform, source) for incremental runs."""

    __tablename__ = "crawl_state"
    __table_args__ = (
        UniqueConstraint("platform", "source", name="uq_crawl_state"),
    )

    id = Column(Integer, primary_key=True)
    platform = Column(Enum(PlatformEnum), nullable=False)
    source = Column(String(255), nullable=False)   # page slug or group ID/slug
    last_crawled_at = Column(DateTime)
    posts_collected = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CrawlState platform={self.platform} source={self.source} last={self.last_crawled_at}>"
