from pathlib import Path
from typing import List, Dict, Any

import fitz


def split_text_into_chunks(
    text: str,
    max_chars: int = 1200,
    overlap: int = 200
) -> List[str]:

    cleaned_text = " ".join(text.split())

    if not cleaned_text:
        return []

    chunks = []
    start = 0

    while start < len(cleaned_text):
        end = start + max_chars
        chunk = cleaned_text[start:end]

        chunks.append(chunk)

        start = end - overlap

        if start < 0:
            start = 0

        if start >= len(cleaned_text):
            break

    return chunks


def extract_chunks_from_pdf(pdf_path: Path, file_name: str) -> List[Dict[str, Any]]:
    """
    Extracts text from PDF page by page and splits each page into chunks.
    """

    all_chunks = []

    try:
        document = fitz.open(pdf_path)
    except Exception as error:
        raise ValueError(f"Could not open PDF file: {error}")

    for page_index in range(len(document)):
        page = document[page_index]
        text = page.get_text("text")

        page_chunks = split_text_into_chunks(text)

        for chunk_index, chunk_text in enumerate(page_chunks):
            all_chunks.append(
                {
                    "file_name": file_name,
                    "page_number": page_index + 1,
                    "chunk_index": chunk_index,
                    "text": chunk_text,
                }
            )

    document.close()

    return all_chunks