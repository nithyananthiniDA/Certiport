from pgvector import Vector

from app.database import get_connection
from app.embeddings import generate_embeddings


def vector_search(
    query: str,
    limit: int = 5,
    document_id: str | None = None,
) -> list[dict]:
    """
    Search document chunks using vector similarity.

    Args:
        query: User's search question.
        limit: Maximum number of results.
        document_id: Optional TEC document ID filter.

    Returns:
        List of matching document chunks with similarity scores.
    """

    # Step 1: Validate the search query
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")

    if limit < 1:
        raise ValueError("Limit must be at least 1")

    # Step 2: Generate embedding for the user's question
    query_embedding = Vector(generate_embeddings([query])[0])

    # Step 3: Build SQL query
    sql = """
        SELECT
            document_id,
            page_number,
            chunk_index,
            content,
            1 - (embedding <=> %s) AS similarity
        FROM document_chunks
    """

    parameters = [query_embedding]

    # Step 4: Apply document filtering directly in PostgreSQL
    if document_id:
        sql += " WHERE document_id = %s"
        parameters.append(document_id)

    # Step 5: Sort by vector similarity
    sql += """
        ORDER BY embedding <=> %s
        LIMIT %s;
    """

    parameters.extend([query_embedding, limit])

    # Step 6: Execute database query
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, parameters)
            rows = cursor.fetchall()

    # Step 7: Convert database rows into dictionaries
    results = []

    for row in rows:
        results.append(
            {
                "document_id": row[0],
                "page_number": row[1],
                "chunk_index": row[2],
                "content": row[3],
                "similarity": float(row[4]),
            }
        )

    return results
