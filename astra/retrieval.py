"""
Astra Triage knowledge-base retrieval.

Offline TF-IDF retrieval (scikit-learn) over the markdown files in
data/knowledge_base/: load -> vectorize -> cosine-similarity search ->
relevance-threshold filter. Kept offline/dependency-light deliberately so
the whole project (including CI) runs without network access or API
keys; the KnowledgeBase interface (search / search_relevant) is the
abstraction boundary a real embedding-backed vector store could swap in
behind later.
"""

from __future__ import annotations

import glob
import os
import re
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from astra import config

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")


@dataclass
class Document:
    id: str
    title: str
    text: str


def _split_into_chunks(text: str) -> list[str]:
    """Sentence/line-level chunks used only for TF-IDF scoring precision.

    Whole-document vectors under-score short, precise queries against long
    articles (a real query scored 0.20 similarity against a ~100-word
    document that a human would call clearly relevant). Splitting into
    chunks for indexing — while still returning the parent Document for
    citation/drafting context — fixes that without losing article-level
    grounding.
    """
    candidates = (
        line.strip()
        for line in _SENTENCE_SPLIT_RE.split(text)
        if line.strip() and not line.strip().startswith("#")
    )
    return [c for c in candidates if len(c) > 5]


def load_documents() -> list[Document]:
    documents = []
    for path in sorted(glob.glob(os.path.join(config.KNOWLEDGE_BASE_DIR, "*.md"))):
        doc_id = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding="utf-8") as f:
            text = f.read()
        title = doc_id
        for line in text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        documents.append(Document(id=doc_id, title=title, text=text))
    return documents


class KnowledgeBase:
    def __init__(self, documents: list[Document] | None = None):
        self.documents = documents if documents is not None else load_documents()
        self._vectorizer = None
        self._matrix = None
        self._chunk_doc_indices: list[int] = []
        if self.documents:
            chunks: list[str] = []
            for doc_index, doc in enumerate(self.documents):
                doc_chunks = _split_into_chunks(doc.text) or [doc.text]
                chunks.extend(doc_chunks)
                self._chunk_doc_indices.extend([doc_index] * len(doc_chunks))
            self._vectorizer = TfidfVectorizer(stop_words="english", sublinear_tf=True)
            self._matrix = self._vectorizer.fit_transform(chunks)

    def search(self, query: str, k: int = 3) -> list[tuple[Document, float]]:
        if not self.documents or self._vectorizer is None:
            return []
        query_vec = self._vectorizer.transform([query])
        chunk_similarities = cosine_similarity(query_vec, self._matrix)[0]

        best_score_per_doc = [0.0] * len(self.documents)
        for chunk_score, doc_index in zip(chunk_similarities, self._chunk_doc_indices):
            if chunk_score > best_score_per_doc[doc_index]:
                best_score_per_doc[doc_index] = float(chunk_score)

        ranked = sorted(
            zip(self.documents, best_score_per_doc), key=lambda pair: pair[1], reverse=True
        )
        return ranked[:k]

    def search_relevant(
        self, query: str, threshold: float | None = None, k: int = 3
    ) -> list[tuple[Document, float]]:
        effective_threshold = config.RETRIEVAL_THRESHOLD if threshold is None else threshold
        return [
            (doc, score) for doc, score in self.search(query, k=k) if score >= effective_threshold
        ]
