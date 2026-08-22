"""
Astra Triage knowledge-base retrieval.

STAGE 2 TODO:
    Implement retrieval over the markdown files in data/knowledge_base/
    using the prescribed pattern: load -> split into documents -> embed
    -> store in a vector store -> similarity search -> apply a relevance
    threshold.

    This repo intentionally keeps embeddings OFFLINE (TF-IDF via
    scikit-learn) rather than calling a real embedding API, so retrieval
    is fully testable without network access. If you have LangChain's
    community vector stores available and want to swap in
    `langchain_community.vectorstores.FAISS` or similar with a real
    embedding function, that's a valid alternative — just keep an offline
    fallback so `pytest` still passes without network/API keys.

    What's missing:

    1. `load_documents()` — read every `*.md` file in
       config.KNOWLEDGE_BASE_DIR into a `Document` (id, title, text).
       Currently returns an empty list.
    2. `KnowledgeBase.__init__` — build the TF-IDF index over the loaded
       documents. Currently does nothing (`self._vectorizer` /
       `self._matrix` stay None), so `search()` will crash.
    3. `KnowledgeBase.search(query, k=3)` — embed the query with the same
       vectorizer, compute cosine similarity against the document matrix,
       return the top-k (document, score) pairs sorted by score
       descending.
    4. `KnowledgeBase.search_relevant(query, threshold=None)` — call
       search(), then filter to only hits with score >= threshold
       (default: config.RETRIEVAL_THRESHOLD). If nothing clears the bar,
       return an empty list — callers use that to decide to escalate.

    Note: `RETRIEVAL_THRESHOLD` currently comes from config as a *string*
    (see the Stage 2 TODO in config.py) — fix that first or this module
    will fail comparing str >= float.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from astra import config


@dataclass
class Document:
    id: str
    title: str
    text: str


def load_documents() -> list[Document]:
    """TODO: load every .md file under config.KNOWLEDGE_BASE_DIR."""
    # Currently a stub — implement me.
    return []


class KnowledgeBase:
    def __init__(self, documents: list[Document] | None = None):
        self.documents = documents if documents is not None else load_documents()
        # TODO: build a TF-IDF (or other offline) vectorizer + matrix here.
        self._vectorizer = None
        self._matrix = None

    def search(self, query: str, k: int = 3) -> list[tuple[Document, float]]:
        """TODO: return top-k (Document, similarity score) pairs."""
        raise NotImplementedError("Implement TF-IDF similarity search (Stage 2).")

    def search_relevant(
        self, query: str, threshold: float | None = None, k: int = 3
    ) -> list[tuple[Document, float]]:
        """TODO: filter search() results to those meeting the relevance threshold."""
        raise NotImplementedError("Implement relevance filtering (Stage 2).")
