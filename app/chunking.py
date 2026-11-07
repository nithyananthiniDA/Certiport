def chunk_pages(pages, chunk_size=500, overlap=75):
    """Split document pages into overlapping word-based chunks."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between zero and chunk_size")

    chunks = []
    step = chunk_size - overlap

    for page in pages:
        words = page.get("text", "").split()

        if not words:
            continue

        chunk_index = 0

        for start in range(0, len(words), step):
            chunk_words = words[start : start + chunk_size]

            chunks.append(
                {
                    "document_id": page["document_id"],
                    "page_number": page["page_number"],
                    "chunk_index": chunk_index,
                    "text": " ".join(chunk_words),
                }
            )

            chunk_index += 1

            if start + chunk_size >= len(words):
                break

    return chunks
