import os
from typing import List

import numpy as np
from openai import OpenAI


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing. Please set it in your .env file.")

    client_settings = {
        "api_key": api_key,
    }

    if base_url:
        client_settings["base_url"] = base_url

    return OpenAI(**client_settings)


def create_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Creates embeddings for a list of text chunks.
    """

    if not texts:
        return []

    client = get_openai_client()
    model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    response = client.embeddings.create(
        model=model,
        input=texts,
    )

    return [item.embedding for item in response.data]


def create_embeddings_for_chunks(chunks: List[dict], batch_size: int = 50) -> List[dict]:
    """
    Adds embedding vectors to PDF chunks.
    Processing is done in batches to avoid sending too much text at once.
    """

    if not chunks:
        return []

    updated_chunks = []
    texts = [chunk["text"] for chunk in chunks]

    for start in range(0, len(texts), batch_size):
        end = start + batch_size

        batch_texts = texts[start:end]
        batch_chunks = chunks[start:end]

        batch_embeddings = create_embeddings(batch_texts)

        for chunk, embedding in zip(batch_chunks, batch_embeddings):
            chunk["embedding"] = embedding
            updated_chunks.append(chunk)

    return updated_chunks


def cosine_similarity(vector_a: List[float], vector_b: List[float]) -> float:
    """
    Calculates cosine similarity between two vectors.
    """

    a = np.array(vector_a, dtype=np.float32)
    b = np.array(vector_b, dtype=np.float32)

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(np.dot(a, b) / (norm_a * norm_b))