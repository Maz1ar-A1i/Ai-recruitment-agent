"""Semantic Search tool using TF-IDF and Cosine Similarity."""
import logging
from typing import Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


def compute_semantic_similarity(
    job_text: str,
    candidate_experience_texts: list[str]
) -> dict:
    """Agent tool: Compute semantic similarity between job requirements and candidate experience."""
    if not job_text or not candidate_experience_texts:
        return {"average_similarity": 0.0, "max_similarity": 0.0, "details": []}

    corpus = [job_text] + candidate_experience_texts
    try:
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(corpus)
        job_vector = tfidf_matrix[0:1]
        exp_vectors = tfidf_matrix[1:]

        similarities = cosine_similarity(job_vector, exp_vectors)[0]
        results = []
        for idx, score in enumerate(similarities):
            results.append({
                "snippet": candidate_experience_texts[idx][:150],
                "similarity_score": round(float(score), 3)
            })

        avg_score = round(float(np.mean(similarities)), 3)
        max_score = round(float(np.max(similarities)), 3)

        return {
            "average_similarity": avg_score,
            "max_similarity": max_score,
            "details": results
        }
    except Exception as e:
        logger.warning("Error computing semantic similarity: %s", e)
        return {"average_similarity": 0.5, "max_similarity": 0.5, "details": []}
