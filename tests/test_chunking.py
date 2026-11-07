from app.chunking import chunk_pages


def test_chunk_pages_creates_overlapping_chunks():
    pages = [{"document_id": "TEST_DOC", "page_number": 1, "text": " ".join(f"word{i}" for i in range(1000))}]

    chunks = chunk_pages(pages, chunk_size=500, overlap=75)

    assert len(chunks) == 3
    assert len(chunks[0]["text"].split()) == 500
    assert len(chunks[1]["text"].split()) == 500
    assert len(chunks[2]["text"].split()) == 150

    assert chunks[0]["document_id"] == "TEST_DOC"
    assert chunks[0]["page_number"] == 1
    assert chunks[0]["chunk_index"] == 0
    assert chunks[1]["chunk_index"] == 1


def test_chunk_pages_handles_empty_text():
    pages = [{"document_id": "TEST_DOC", "page_number": 1, "text": ""}]

    assert chunk_pages(pages) == []
