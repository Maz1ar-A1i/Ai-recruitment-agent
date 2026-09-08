"""Document processor for knowledge base text chunking."""
import re
from typing import List


def chunk_text(text: str, chunk_size: int = 400, chunk_overlap: int = 80) -> list[str]:
    """Split long document text into overlapping paragraph-aware chunks."""
    clean_text = re.sub(r"\s+", " ", text).strip()
    if not clean_text:
        return []

    words = clean_text.split(" ")
    if len(words) <= chunk_size:
        return [clean_text]

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end == len(words):
            break
        start += (chunk_size - chunk_overlap)

    return chunks
