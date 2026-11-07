from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query

from app.config import Settings, get_settings
from app.hybrid_clause_search import hybrid_clause_search
from app.llm import generate_answer, get_usage
from app.schemas import AskRequest, AskResponse
from app.search import TelecomSearch

app = FastAPI(
    title="CertiPort Telecom Search",
    description="AI-powered telecom certification document search and assistant.",
    version="0.9.0",
)


_search_engine = None


def get_search_engine() -> TelecomSearch:
    """Create and reuse the telecom document search engine."""
    global _search_engine

    if _search_engine is None:
        _search_engine = TelecomSearch()

    return _search_engine


@app.get("/")
def root():
    return {
        "message": "Welcome to CertiPort Telecom Search API",
        "version": "0.9.0",
    }


@app.get("/health")
def health(
    settings: Annotated[Settings, Depends(get_settings)],
):
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
    }


@app.get("/search")
def search_documents(
    q: str = Query(
        min_length=1,
        description="Search TEC document pages.",
    ),
    limit: int = Query(default=5, ge=1, le=20),
    document_id: str | None = None,
):
    """Search TEC document pages using BM25."""

    query = q.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty.",
        )

    engine = get_search_engine()

    results = engine.search(
        query=query,
        limit=limit,
        document_id=document_id,
    )

    return {
        "query": query,
        "search_method": "BM25",
        "total_results": len(results),
        "results": results,
    }


@app.get("/clauses/search")
def search_clauses(
    q: str = Query(
        min_length=1,
        description="Search TEC document clauses.",
    ),
    limit: int = Query(default=5, ge=1, le=20),
    document_id: str | None = None,
):
    """Search individual TEC clauses using BM25."""

    query = q.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Clause search query cannot be empty.",
        )

    engine = get_search_engine()

    results = engine.search_clauses(
        query=query,
        limit=limit,
        document_id=document_id,
    )

    return {
        "query": query,
        "search_method": "BM25 clause-level",
        "total_results": len(results),
        "results": results,
    }


@app.get("/hybrid-search")
def search_hybrid(
    q: str = Query(
        min_length=1,
        description="Search using BM25 and vector retrieval.",
    ),
    limit: int = Query(default=5, ge=1, le=10),
    document_id: str | None = None,
):
    """Search TEC clauses using hybrid BM25 and vector retrieval."""

    query = q.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty.",
        )

    engine = get_search_engine()

    try:
        results = hybrid_clause_search(
            query=query,
            search_engine=engine,
            limit=limit,
            document_id=document_id,
        )

    except (ValueError, OSError, RuntimeError) as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Hybrid search is unavailable: {str(exc)}",
        ) from exc

    return {
        "query": query,
        "search_method": "Hybrid BM25 + Vector + RRF",
        "total_results": len(results),
        "results": results,
    }


def generate_certification_answer(
    query: str,
    limit: int = 5,
    document_id: str | None = None,
) -> dict:
    """Retrieve TEC clauses and generate an answer with citations."""

    engine = get_search_engine()
    search_method = "Hybrid BM25 + Vector + RRF"

    if hasattr(engine, "clauses"):
        try:
            results = hybrid_clause_search(
                query=query,
                search_engine=engine,
                limit=limit,
                document_id=document_id,
            )

        except Exception:
            results = engine.search_clauses(
                query=query,
                limit=limit,
                document_id=document_id,
            )

            search_method = "BM25 clause-level fallback"

    else:
        results = engine.search_clauses(
            query=query,
            limit=limit,
            document_id=document_id,
        )

        search_method = "BM25 clause-level"

    if not results:
        return {
            "question": query,
            "answer": "No relevant TEC document clauses were found.",
            "search_method": search_method,
            "answer_source": "none",
            "citations": [],
        }

    context_parts = []
    citations = []

    for result in results:
        context_parts.append(
            f"Document: {result['document_id']}\n"
            f"Page: {result['page_number']}\n"
            f"Clause: {result['clause_number']}\n"
            f"Title: {result['clause_title']}\n"
            f"Text: {result['matched_text']}"
        )

        citations.append(
            {
                "document_id": result["document_id"],
                "page_number": result["page_number"],
                "clause_number": result["clause_number"],
                "clause_title": result["clause_title"],
            }
        )

    context = "\n\n".join(context_parts)

    try:
        try:
            generated = generate_answer(
                question=query,
                context=context,
                return_provider=True,
            )

        except TypeError as exc:
            if "return_provider" not in str(exc):
                raise

            generated = generate_answer(
                question=query,
                context=context,
            )

        if isinstance(generated, tuple):
            answer, answer_source = generated
        else:
            answer = generated
            answer_source = "openai"

    except ValueError:
        answer = (
            "AI-generated answer is currently unavailable. "
            "The following information was retrieved directly "
            "from the TEC documents:\n\n" + "\n\n".join(context_parts)
        )

        answer_source = "tec_document_fallback"

    return {
        "question": query,
        "answer": answer,
        "search_method": search_method,
        "answer_source": answer_source,
        "citations": citations,
    }


@app.get("/ask")
def ask_certification_question(
    q: str = Query(
        min_length=1,
        description="Ask a telecom certification question.",
    ),
    limit: int = Query(default=5, ge=1, le=10),
    document_id: str | None = None,
) -> dict:
    """Answer questions using hybrid-retrieved TEC clauses."""

    query = q.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    return generate_certification_answer(
        query=query,
        limit=limit,
        document_id=document_id,
    )


@app.post("/ask", response_model=AskResponse)
def ask_certification_question_post(
    request: AskRequest,
) -> AskResponse:
    """Answer telecom certification questions using a JSON request."""

    query = request.question.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    result = generate_certification_answer(
        query=query,
        limit=request.limit,
        document_id=request.document_id,
    )

    return AskResponse(**result)


@app.get("/usage")
def usage():
    """Return LLM token and cost usage information."""

    return get_usage()
