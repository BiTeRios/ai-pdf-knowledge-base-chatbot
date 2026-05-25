from typing import List, Dict, Any

from app.embedding_service import create_embeddings, cosine_similarity


def retrieve_relevant_chunks(
    question: str,
    chunks: List[Dict[str, Any]],
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Finds the most relevant chunks using embeddings + cosine similarity.
    """

    if not chunks:
        return []

    chunks_with_embeddings = [
        chunk for chunk in chunks
        if chunk.get("embedding") is not None
    ]

    if not chunks_with_embeddings:
        return []

    question_embedding = create_embeddings([question])[0]

    scored_chunks = []

    for chunk in chunks_with_embeddings:
        score = cosine_similarity(
            question_embedding,
            chunk["embedding"],
        )

        chunk_copy = chunk.copy()
        chunk_copy["score"] = score

        scored_chunks.append(chunk_copy)

    scored_chunks.sort(key=lambda item: item["score"], reverse=True)

    relevant_chunks = [
        chunk for chunk in scored_chunks
        if chunk["score"] > 0.2
    ]

    return relevant_chunks[:top_k]