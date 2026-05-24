import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")


def generate_answer(question: str, chunks: list) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set")

    context = "\n\n".join(
        [
            f"Source: {chunk.get('file_name', 'unknown')}, page {chunk.get('page_number', 'unknown')}\n{chunk.get('text', '')}"
            for chunk in chunks
        ]
    )

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {
                "role": "system",
                "content": (
                    "You are a PDF knowledge base assistant. "
                    "Answer only using the provided context. "
                    "If the context does not contain the answer, say that the information was not found in the uploaded documents."
                ),
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{question}",
            },
        ],
    )

    return response.output_text