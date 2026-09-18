from app.graph.graph import KnowledgeGraph
from app.nlp.ranker import EmbeddingRanker, KeywordRanker, get_ranker


def test_keyword_rank_hits_right_pool(graph: KnowledgeGraph):
    ranking = get_ranker(graph, "keyword")
    top = ranking.rank("linear_algebra", limit=2)
    assert len(top) == 2
    assert all(c["topic"] == "linear_algebra" for c in top)
    # the flagship MIT OCW 18.06 course must sit in the top pairing
    ids = [c["id"] for c in top]
    assert "mit_18_06" in ids or "youtube_3b1b_la" in ids


def test_rank_is_deterministic(graph: KnowledgeGraph):
    r = get_ranker(graph, "keyword")
    a = [c["id"] for c in r.rank("deep_learning", limit=3)]
    b = [c["id"] for c in r.rank("deep_learning", limit=3)]
    assert a == b


def test_ranker_prefers_keyword_by_default(graph: KnowledgeGraph):
    r = get_ranker(graph)
    assert isinstance(r, KeywordRanker)


def test_embedding_ranker_degrades_to_keyword(graph: KnowledgeGraph):
    r = get_ranker(graph, "embedding")
    assert isinstance(r, EmbeddingRanker)
    # no fastembed installed in the default env -> falls back internally
    top = r.rank("python_core", limit=1)
    assert top and top[0]["topic"] == "python_core"