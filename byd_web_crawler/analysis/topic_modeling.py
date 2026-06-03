"""
BERTopic-based topic modeling for BYD perception data.

Usage:
    from analysis.topic_modeling import TopicModeler
    modeler = TopicModeler()
    topics, probs, info = modeler.fit_transform(texts)
    modeler.save("models/topic_model")
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _tokenize_thai(text: str) -> str:
    """Word-segment Thai text so BERTopic's vectorizer sees tokens."""
    try:
        from pythainlp.tokenize import word_tokenize
        return " ".join(word_tokenize(text, engine="newmm"))
    except ImportError:
        return text


class TopicModeler:
    def __init__(self, n_topics: int = 10, min_topic_size: int = 5):
        from bertopic import BERTopic
        from sklearn.feature_extraction.text import CountVectorizer

        # Stop-words list for Thai (minimal)
        _TH_STOPWORDS = [
            "ที่", "และ", "ใน", "มี", "ก็", "แต่", "จะ", "ได้", "ให้", "กับ",
            "ของ", "เป็น", "ว่า", "ไม่", "มา", "นี้", "นั้น", "ไป", "แล้ว",
            "อยู่", "ต้อง", "ก่อน", "หาก", "เมื่อ", "หรือ", "น่า",
        ]

        vectorizer = CountVectorizer(
            stop_words=_TH_STOPWORDS,
            ngram_range=(1, 2),
            min_df=2,
        )
        self._model = BERTopic(
            language="multilingual",
            nr_topics=n_topics,
            min_topic_size=min_topic_size,
            vectorizer_model=vectorizer,
            calculate_probabilities=True,
            verbose=True,
        )
        self._fitted = False

    # ------------------------------------------------------------------

    def fit_transform(self, texts: list[str]) -> tuple:
        """
        Returns (topics, probs, topic_info_df).
        texts: raw post/comment strings (Thai or English).
        """
        logger.info("Tokenizing %d texts for topic modeling...", len(texts))
        processed = [_tokenize_thai(t) for t in texts]

        logger.info("Fitting BERTopic...")
        topics, probs = self._model.fit_transform(processed)
        self._fitted = True

        info = self._model.get_topic_info()
        logger.info("Found %d topics (excl. outlier topic -1)", len(info) - 1)
        return topics, probs, info

    def get_topic_words(self, topic_id: int, top_n: int = 10) -> list[tuple[str, float]]:
        return self._model.get_topic(topic_id)[:top_n]

    def get_representative_docs(self, topic_id: int) -> list[str]:
        return self._model.get_representative_docs(topic_id)

    def save(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._model.save(path)
        logger.info("Topic model saved to %s", path)

    @classmethod
    def load(cls, path: str) -> "TopicModeler":
        from bertopic import BERTopic
        instance = cls.__new__(cls)
        instance._model = BERTopic.load(path)
        instance._fitted = True
        return instance

    # ------------------------------------------------------------------

    def run_from_db(self, session) -> tuple:
        """Convenience: pull all post contents from DB and fit."""
        from storage.models import Post
        posts = session.query(Post).all()
        texts = [p.content for p in posts if p.content]
        if len(texts) < 10:
            raise ValueError(f"Need at least 10 posts for topic modeling, got {len(texts)}")
        return self.fit_transform(texts)
