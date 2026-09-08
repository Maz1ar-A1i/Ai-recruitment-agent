"""Lightweight RAG Retriever and Vector Store."""
import logging
from typing import Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.schemas.knowledge import KnowledgeQueryResult

logger = logging.getLogger(__name__)


class LightweightVectorStore:
    """In-memory lightweight vector store supporting dynamic addition and semantic retrieval."""

    def __init__(self):
        self._chunks: list[dict] = []

    def add_chunk(self, chunk_id: str, document_title: str, document_type: str, content: str, metadata: Optional[dict] = None):
        self._chunks.append({
            "chunk_id": chunk_id,
            "document_title": document_title,
            "document_type": document_type,
            "content": content,
            "metadata": metadata or {}
        })

    def delete_by_document_id(self, document_id: str):
        self._chunks = [c for c in self._chunks if c.get("metadata", {}).get("document_id") != document_id]

    def clear(self):
        self._chunks.clear()

    def query(self, query_text: str, top_k: int = 3) -> list[KnowledgeQueryResult]:
        if not self._chunks or not query_text.strip():
            return []

        corpus = [c["content"] for c in self._chunks]
        try:
            vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform(corpus)
            query_vec = vectorizer.transform([query_text])

            sims = cosine_similarity(query_vec, tfidf_matrix)[0]
            top_indices = sims.argsort()[::-1][:top_k]

            results = []
            for idx in top_indices:
                score = float(sims[idx])
                if score > 0.05:  # Relevance threshold
                    chunk = self._chunks[idx]
                    results.append(KnowledgeQueryResult(
                        chunk_id=chunk["chunk_id"],
                        document_title=chunk["document_title"],
                        document_type=chunk["document_type"],
                        content=chunk["content"],
                        similarity_score=round(score, 3)
                    ))
            return results
        except Exception as e:
            logger.warning("RAG retrieval error: %s", e)
            return []


# Singleton in-memory store
rag_store = LightweightVectorStore()
