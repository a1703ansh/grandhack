"""Course ranking per topic.

Default is a deterministic pure-Python TF-IDF keyword ranker (zero model,
zero downloads, runs everywhere). When fastembed is installed AND
CF_USE_EMBEDDINGS=1, ranking uses real sentence embeddings (Tier-2) with a
keyword fallback on any failure — the runtime stays light by default.
"""

from __future__ import annotations

import math
import os
import re
from collections import Counter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.graph.graph import KnowledgeGraph

_STOPWORDS = {
    "the", "and", "for", "with", "from", "this", "that", "course", "courses",
    "using", "free", "online", "learn", "learning", "an", "a", "of", "to",
    "in", "on", "you", "are", "is", "was", "be",
}


def _tokenize(text: str) -> list[str]:
    return [
        t
        for t in re.split(r"[^a-z0-9]+", text.lower())
        if len(t) > 1 and t not in _STOPWORDS
    ]


def _cosine(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    dot = sum(a[k] * b.get(k, 0) for k in a)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


class CourseRanker:
    """Base ranker. Subclasses implement `_score(query, candidate) -> float`."""

    def __init__(self, graph: "KnowledgeGraph"):
        self.graph = graph

    def rank(self, topic_id: str, limit: int = 2) -> list[dict]:
        candidates = self.graph.courses_by_topic.get(topic_id, [])
        if not candidates:
            return []
        query = self._query_for(topic_id)
        scored = []
        for c in candidates:
            text = f"{c['title']} {c.get('keywords', '')} {' '.join(c.get('tags', []))}"
            scored.append((self._score(query, text), c))
        scored.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
        top = [c for _, c in scored[:limit]]
        # keep deterministic
        return top

    def _query_for(self, topic_id: str) -> str:
        t = self.graph.topics[topic_id]
        return f"{t['name']}. {t.get('description', '')}. {t.get('why', '')}"

    def _score(self, query: str, candidate: str) -> float:
        raise NotImplementedError


class KeywordRanker(CourseRanker):
    """TF-IDF cosine over the course corpus. Pure python, deterministic."""

    def __init__(self, graph: "KnowledgeGraph"):
        super().__init__(graph)
        docs = [
            f"{c['title']} {c.get('keywords', '')} {' '.join(c.get('tags', []))}"
            for c in graph.courses
        ]
        df: Counter = Counter()
        for d in docs:
            df.update(set(_tokenize(d)))
        n = max(len(docs), 1)
        self.idf = {
            term: math.log(1 + n / count)
            for term, count in df.items()
        }

    def _vector(self, text: str) -> Counter:
        counts = Counter(_tokenize(text))
        tf = counts
        return {term: (tf[term] * self.idf.get(term, 0.0)) for term in tf}

    def _score(self, query: str, candidate: str) -> float:
        return _cosine(Counter(self._vector(query)), Counter(self._vector(candidate)))


class EmbeddingRanker(CourseRanker):
    """Sentence-embedding cosine (fastembed / ONNX). Lazy model load."""

    def __init__(self, graph: "KnowledgeGraph"):
        super().__init__(graph)
        self._model = None
        self.kw = KeywordRanker(graph)
        self._enabled = self._try_load()

    def _try_load(self) -> bool:
        if os.environ.get("CF_USE_EMBEDDINGS") != "1":
            return False
        try:
            from fastembed import TextEmbedding  # noqa: PLC0415

            self._model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")
            return True
        except Exception:
            return False

    def _embed(self, texts: list[str]):
        return list(self._model.embed(texts))

    def _score(self, query: str, candidate: str) -> float:
        if not self._enabled or self._model is None:
            return self.kw._score(query, candidate)
        try:
            [q], [c] = self._embed([query]), self._embed([candidate])
            return float(_cosine(Counter(enumerate(q)), Counter(enumerate(c))))
        except Exception:
            return self.kw._score(query, candidate)


_RANKER_CACHE: dict[str, CourseRanker] = {}


def get_ranker(graph: "KnowledgeGraph", forced: str | None = None) -> CourseRanker:
    mode = (forced or os.environ.get("CF_RANKER", "keyword")).lower()
    key = (mode, id(graph))
    if key not in _RANKER_CACHE:
        if mode == "embedding":
            _RANKER_CACHE[key] = EmbeddingRanker(graph)
        else:
            _RANKER_CACHE[key] = KeywordRanker(graph)
    return _RANKER_CACHE[key]