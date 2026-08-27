"""
STAGE 4 TODO: these tests exercise the Stage-2 retrieval implementation.
They should fail against the retrieval.py stub and pass once
load_documents / KnowledgeBase.search / search_relevant are implemented.
"""

from astra.retrieval import KnowledgeBase, load_documents


def test_load_documents_finds_kb_files():
    docs = load_documents()
    assert len(docs) >= 4
    titles = {d.id for d in docs}
    assert any("billing" in t for t in titles)


def test_search_returns_relevant_billing_doc():
    kb = KnowledgeBase()
    results = kb.search("I was charged twice for my subscription", k=3)
    assert results, "expected at least one result"
    top_doc, top_score = results[0]
    assert "billing" in top_doc.id


def test_search_relevant_filters_low_scores():
    kb = KnowledgeBase()
    results = kb.search_relevant("purple giraffe skateboard wizard", threshold=0.3)
    assert results == []


def test_search_relevant_default_threshold_from_config():
    kb = KnowledgeBase()
    results = kb.search_relevant("account locked out password reset")
    assert results
    for _doc, score in results:
        assert score >= 0
