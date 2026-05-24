from typing import List, Dict, Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def retrieve_relevant_chunks(
    question: str,
    chunks: List[Dict[str, Any]],
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Finds the most relevant chunks for the user's question.

    This version uses TF-IDF + cosine similarity.
    """

    if not chunks:
        return []

    texts = [chunk["text"] for chunk in chunks]

    try:
        vectorizer = TfidfVectorizer()
        matrix = vectorizer.fit_transform(texts + [question])

        question_vector = matrix[-1]
        chunk_vectors = matrix[:-1]

        similarities = cosine_similarity(question_vector, chunk_vectors).flatten()

    except ValueError:
        return []

    scored_chunks = []

    for index, chunk in enumerate(chunks):
        chunk_copy = chunk.copy()
        chunk_copy["score"] = float(similarities[index])
        scored_chunks.append(chunk_copy)

    scored_chunks.sort(key=lambda item: item["score"], reverse=True)

    relevant_chunks = [
        chunk for chunk in scored_chunks
        if chunk["score"] > 0
    ]

    return relevant_chunks[:top_k]