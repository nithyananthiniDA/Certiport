from app.search import TelecomSearch, normalize_document_id
from app.vector_search import vector_search


def hybrid_clause_search(
    query: str,
    search_engine: TelecomSearch,
    limit: int = 5,
    document_id: str | None = None,
) -> list[dict]:

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")

    if limit < 1:
        raise ValueError("Limit must be at least 1")

    k = 60

    # Step 1: BM25 clause retrieval
    bm25_results = search_engine.search_clauses(
        query=query,
        limit=limit * 3,
        document_id=document_id,
    )

    # Step 2: Vector semantic retrieval
    vector_results = vector_search(
        query=query,
        limit=limit * 3,
        document_id=document_id,
    )

    combined = {}

    # Step 3: Add BM25 ranking contributions
    for rank, result in enumerate(bm25_results, start=1):
        key = (
            normalize_document_id(result["document_id"]),
            result["page_number"],
            result["clause_number"],
        )

        combined[key] = {
            **result,
            "rrf_score": 1.0 / (k + rank),
            "sources": ["BM25"],
        }

    # Step 4: Keep the best vector result for each page
    best_vector_pages = {}

    for rank, result in enumerate(vector_results, start=1):
        page_key = (
            normalize_document_id(result["document_id"]),
            result["page_number"],
        )

        if page_key not in best_vector_pages:
            best_vector_pages[page_key] = {
                "rank": rank,
                "result": result,
            }

    # Step 5: Map vector pages to clauses
    clauses_by_page = {}

    for clause in search_engine.clauses:
        clause_document = normalize_document_id(
            clause.get("document_id", "")
        )

        if document_id and clause_document != normalize_document_id(document_id):
            continue

        page_key = (
            clause_document,
            clause.get("page_number"),
        )

        clauses_by_page.setdefault(page_key, []).append(clause)

    # Step 6: Add vector contributions to clause rankings
    for page_key, vector_item in best_vector_pages.items():
        page_clauses = clauses_by_page.get(page_key, [])

        if not page_clauses:
            continue

        vector_rank = vector_item["rank"]
        vector_result = vector_item["result"]

        # Divide the page contribution among its clauses.
        page_contribution = (
            1.0 / (k + vector_rank)
        ) / len(page_clauses)

        for clause in page_clauses:
            key = (
                page_key[0],
                clause["page_number"],
                clause["clause_number"],
            )

            if key not in combined:
                combined[key] = {
                    "document_id": clause["document_id"],
                    "page_number": clause["page_number"],
                    "clause_number": clause["clause_number"],
                    "clause_title": clause["clause_title"],
                    "matched_text": clause.get("text", "")[:1000],
                    "rrf_score": 0.0,
                    "sources": [],
                }

            combined[key]["rrf_score"] += page_contribution

            if "Vector" not in combined[key]["sources"]:
                combined[key]["sources"].append("Vector")

            combined[key]["similarity"] = vector_result["similarity"]

    # Step 7: Sort by combined RRF score
    ranked_results = sorted(
        combined.values(),
        key=lambda item: item["rrf_score"],
        reverse=True,
    )

    return ranked_results[:limit]
