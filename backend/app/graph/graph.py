"""Knowledge graph over the curated seed.

Pure-python adjacency (no NetworkX): dicts + BFS/topological order. The graph
is a DAG where edge `from -> to` means "from is required before to".
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from typing import Any


class KnowledgeGraph:
    def __init__(self, seed: dict):
        self.topics: dict[str, dict] = seed["topics"]
        self.edges: list[dict] = seed["edges"]
        self.courses: list[dict] = seed["courses"]
        self.aliases: dict[str, list[str]] = seed.get("aliases", {})
        self.goal_id_order: list[str] = seed.get("goal_id_order", [])
        self.embeddings: dict[str, list[float]] = seed.get("embeddings", {})
        self.embedding_dim: int = seed.get("embedding_dim", 0)

        self.adj: dict[str, set[str]] = defaultdict(set)
        self.reverse: dict[str, set[str]] = defaultdict(set)
        for e in self.edges:
            self.adj[e["from"]].add(e["to"])
            self.reverse[e["to"]].add(e["from"])

        self._alias_lookup: dict[str, str] = {}
        for topic_id, words in self.aliases.items():
            for w in words:
                self._alias_lookup[w.strip().lower()] = topic_id

        # word-boundary patterns so "py" never matches inside "numpy"
        self._alias_patterns: list[tuple[re.Pattern, int, str]] = [
            (re.compile(rf"\b{re.escape(a)}\b"), len(a), tid)
            for a, tid in self._alias_lookup.items()
        ]

        self.courses_by_topic: dict[str, list[dict]] = defaultdict(list)
        for c in self.courses:
            self.courses_by_topic[c["topic"]].append(c)

    # ------------------------------------------------------------ loading
    @classmethod
    def from_file(cls, path) -> "KnowledgeGraph":
        return cls(json.loads(path.read_text(encoding="utf-8")))

    # --------------------------------------------------------- resolution
    def _alias_matches(self, text: str) -> set[str]:
        """Canonical topic ids whose alias appears as a whole word in text."""
        matched: set[str] = set()
        for pattern, _len, tid in self._alias_patterns:
            if pattern.search(text):
                matched.add(tid)
        return matched

    def resolve_topic(self, text: str) -> str | None:
        """Map free-text goal/background to a canonical topic id."""
        t = text.strip().lower()
        if not t:
            return None
        if t in self._alias_lookup:
            return self._alias_lookup[t]
        matched = self._alias_matches(t)
        if matched:
            # most specific alias wins (deep_learning beats ml when both appear)
            best, best_len = None, -1
            for pattern, alen, tid in self._alias_patterns:
                if tid in matched and alen > best_len and pattern.search(t):
                    best_len, best = alen, tid
            return best
        # token overlap against topic names (fuzzy goal fallback)
        tokens = {
            tok
            for tok in re.split(r"[^a-z0-9]+", t)
            if tok and tok not in _STOPWORDS
        }
        if tokens:
            for topic_id in self.goal_id_order:
                tname = self.topics[topic_id]["name"].lower()
                if tokens & set(re.split(r"[^a-z0-9]+", tname)):
                    return topic_id
        return None

    def satisfied_topics(self, current_knowledge: str) -> set[str]:
        """Break free-text background into satisfied topic ids."""
        if not current_knowledge:
            return set()
        t = current_knowledge.lower()
        all_matches = self._alias_matches(t)
        if all_matches:
            return all_matches
        parts = re.split(r"[,;+]| and |, and | plus ", t)
        resolved: set[str] = set()
        for part in parts:
            tid = self.resolve_topic(part)
            if tid:
                resolved.add(tid)
        return resolved


_STOPWORDS = {
    "a", "an", "the", "i", "want", "to", "learn", "master", "know", "knows",
    "have", "with", "for", "and", "of", "in", "on", "my", "me", "about",
    "some", "basic", "basics", "fundamentals", "am", "is", "are", "do", "going",
    "im", "i'm", "please", "help", "build", "become", "understanding",
}