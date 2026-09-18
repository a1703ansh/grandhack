"""Optional sentence-embedding backend (fastembed / ONNX Runtime).

Kept separate from ranker so the served app never imports torch or a model
unless explicitly enabled. The seed-time build writes a precomputed matrix
for reference; runtime embedding is lazy and off by default.
"""

from __future__ import annotations


def require_fastembed():
    """Import and return TextEmbedding; raises ImportError if unavailable."""
    try:
        from fastembed import TextEmbedding  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover - simple passthrough
        raise ImportError(
            "fastembed is not installed. Install optional deps: "
            "pip install fastembed"
        ) from exc
    return TextEmbedding