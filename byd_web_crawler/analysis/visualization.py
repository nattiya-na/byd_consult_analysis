"""
Visualization helpers — Plotly charts + word clouds for BYD perception data.

All functions accept a SQLAlchemy session and return Plotly figures
(or write files directly if save_path is given).
"""

import logging
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

def _load_sentiment_df(session) -> pd.DataFrame:
    """Return a flat DataFrame of posts + their sentiment results."""
    from storage.models import Post, SentimentResult

    rows = (
        session.query(Post, SentimentResult)
        .outerjoin(SentimentResult, SentimentResult.post_id == Post.id)
        .all()
    )
    records = []
    for post, sr in rows:
        records.append({
            "platform": post.platform.value if post.platform else "unknown",
            "published_at": post.published_at,
            "likes": post.likes or 0,
            "views": post.views or 0,
            "fast_sentiment": sr.fast_sentiment.value if sr and sr.fast_sentiment else None,
            "llm_sentiment": sr.llm_sentiment.value if sr and sr.llm_sentiment else None,
            "aspects": sr.aspects if sr else {},
            "key_concerns": sr.key_concerns if sr else [],
            "key_praises": sr.key_praises if sr else [],
            "summary": sr.llm_summary if sr else "",
            "content": post.content or "",
        })
    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# Chart builders
# ---------------------------------------------------------------------------

def sentiment_by_platform(session, save_path: str | None = None) -> go.Figure:
    """Grouped bar chart: sentiment counts per platform."""
    df = _load_sentiment_df(session)
    col = "llm_sentiment" if df["llm_sentiment"].notna().any() else "fast_sentiment"
    df = df[df[col].notna()]

    counts = df.groupby(["platform", col]).size().reset_index(name="count")
    fig = px.bar(
        counts,
        x="platform",
        y="count",
        color=col,
        barmode="group",
        color_discrete_map={
            "positive": "#2ecc71",
            "neutral":  "#95a5a6",
            "negative": "#e74c3c",
        },
        title="BYD Sentiment by Platform",
        labels={"platform": "Platform", "count": "Posts", col: "Sentiment"},
    )
    fig.update_layout(legend_title_text="Sentiment")
    if save_path:
        fig.write_html(save_path)
    return fig


def sentiment_timeline(session, save_path: str | None = None) -> go.Figure:
    """Line chart: sentiment ratio over time (monthly)."""
    df = _load_sentiment_df(session)
    col = "llm_sentiment" if df["llm_sentiment"].notna().any() else "fast_sentiment"
    df = df[(df[col].notna()) & (df["published_at"].notna())].copy()
    df["month"] = pd.to_datetime(df["published_at"]).dt.to_period("M").astype(str)

    pivot = (
        df.groupby(["month", col])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    fig = go.Figure()
    color_map = {"positive": "#2ecc71", "neutral": "#95a5a6", "negative": "#e74c3c"}
    for sentiment in ["positive", "neutral", "negative"]:
        if sentiment in pivot.columns:
            fig.add_trace(go.Scatter(
                x=pivot["month"],
                y=pivot[sentiment],
                name=sentiment.capitalize(),
                mode="lines+markers",
                line=dict(color=color_map[sentiment]),
            ))

    fig.update_layout(
        title="BYD Sentiment Over Time",
        xaxis_title="Month",
        yaxis_title="Post Count",
        legend_title="Sentiment",
    )
    if save_path:
        fig.write_html(save_path)
    return fig


def aspect_heatmap(session, save_path: str | None = None) -> go.Figure:
    """Heatmap of aspect sentiments across platforms."""
    df = _load_sentiment_df(session)
    df = df[df["aspects"].apply(lambda x: bool(x))]

    from config.keywords import SENTIMENT_ASPECTS

    # Encode aspect values numerically
    _SCORE = {"positive": 1, "neutral": 0, "negative": -1, "not_mentioned": None}

    rows = []
    for _, row in df.iterrows():
        for asp in SENTIMENT_ASPECTS:
            val = (row["aspects"] or {}).get(asp)
            rows.append({
                "platform": row["platform"],
                "aspect": asp,
                "score": _SCORE.get(val),
            })

    asp_df = pd.DataFrame(rows).dropna(subset=["score"])
    if asp_df.empty:
        logger.warning("No aspect data available for heatmap")
        return go.Figure()

    pivot = asp_df.groupby(["platform", "aspect"])["score"].mean().unstack()

    fig = px.imshow(
        pivot,
        color_continuous_scale=["#e74c3c", "#ecf0f1", "#2ecc71"],
        zmin=-1, zmax=1,
        title="Average Aspect Sentiment by Platform (−1=Neg, 0=Neutral, +1=Pos)",
        labels={"color": "Avg Sentiment"},
        aspect="auto",
    )
    if save_path:
        fig.write_html(save_path)
    return fig


def top_concerns_and_praises(session, top_n: int = 15, save_path: str | None = None) -> go.Figure:
    """Horizontal bar charts for most common concerns and praises."""
    df = _load_sentiment_df(session)

    from collections import Counter
    concerns = Counter()
    praises = Counter()

    for row in df.itertuples():
        for c in (row.key_concerns or []):
            concerns[c] += 1
        for p in (row.key_praises or []):
            praises[p] += 1

    fig = make_subplots(rows=1, cols=2, subplot_titles=["Top Concerns", "Top Praises"])

    if concerns:
        top_c = pd.DataFrame(concerns.most_common(top_n), columns=["item", "count"])
        fig.add_trace(go.Bar(x=top_c["count"], y=top_c["item"], orientation="h",
                             marker_color="#e74c3c", name="Concerns"), row=1, col=1)

    if praises:
        top_p = pd.DataFrame(praises.most_common(top_n), columns=["item", "count"])
        fig.add_trace(go.Bar(x=top_p["count"], y=top_p["item"], orientation="h",
                             marker_color="#2ecc71", name="Praises"), row=1, col=2)

    fig.update_layout(title_text="BYD — Top Concerns vs. Praises", showlegend=False)
    if save_path:
        fig.write_html(save_path)
    return fig


def wordcloud_by_sentiment(session, output_dir: str = "outputs/wordclouds") -> None:
    """Generate PNG word clouds split by sentiment class."""
    try:
        from wordcloud import WordCloud
        import matplotlib.pyplot as plt
    except ImportError:
        logger.warning("wordcloud / matplotlib not installed; skipping word clouds")
        return

    try:
        from pythainlp.tokenize import word_tokenize
        def tokenize(text): return " ".join(word_tokenize(text, engine="newmm"))
    except ImportError:
        def tokenize(text): return text

    df = _load_sentiment_df(session)
    col = "llm_sentiment" if df["llm_sentiment"].notna().any() else "fast_sentiment"

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for sentiment in ["positive", "neutral", "negative"]:
        subset = df[df[col] == sentiment]
        if subset.empty:
            continue
        combined = " ".join(subset["content"].dropna().tolist())
        combined = tokenize(combined)
        wc = WordCloud(
            width=1200, height=600,
            background_color="white",
            max_words=150,
            font_path=None,   # set a Thai-compatible font path if needed
            colormap="RdYlGn" if sentiment != "neutral" else "Blues",
        ).generate(combined)
        out_path = f"{output_dir}/{sentiment}.png"
        wc.to_file(out_path)
        logger.info("Saved word cloud → %s", out_path)


# ---------------------------------------------------------------------------
# Full dashboard
# ---------------------------------------------------------------------------

def build_dashboard(session, output_dir: str = "outputs") -> None:
    """Generate all charts and save to output_dir."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    sentiment_by_platform(session, save_path=f"{output_dir}/sentiment_by_platform.html")
    sentiment_timeline(session, save_path=f"{output_dir}/sentiment_timeline.html")
    aspect_heatmap(session, save_path=f"{output_dir}/aspect_heatmap.html")
    top_concerns_and_praises(session, save_path=f"{output_dir}/concerns_vs_praises.html")
    wordcloud_by_sentiment(session, output_dir=f"{output_dir}/wordclouds")

    logger.info("Dashboard written to %s/", output_dir)
