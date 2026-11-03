
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query

from app.config import Settings, get_settings
from app.llm import generate_answer, get_usage
from app.search import TelecomSearch

app = FastAPI(
    title="CertiPort Telecom Search",
    description=(
        "AI-powered telecom certification assistant "
        "using TEC documents."
    ),
    version="0.7.0",
)

SettingsDep = Annotated[Settings, Depends(get_settings)]

_search_engine: TelecomSearch | None = None


def get_search_engine() -> TelecomSearch:
    """Load the search engine when needed."""

    global _search_engine

    if _search_engine is None:
        try:
            _search_engine = TelecomSearch()

        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=503,
                detail="TEC document data is not available.",
            ) from exc

        except (OSError, ValueError) as exc:
            raise HTTPException(
                status_code=500,
                detail="Could not load TEC document data.",
            ) from exc

    return _search_engine


@app.get("/health")
def health(settings: SettingsDep) -> dict:
    """Check application status."""

    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
    }


@app.get("/usage")
def usage() -> dict:
    """Return accumulated LLM token usage and estimated cost."""

    return get_usage()


@app.get("/search")
def search_document(
    q: str = Query(min_length=1),
    limit: int = Query(default=10, ge=1, le=50),
    document_id: str | None = None,
) -> dict:
    """Search TEC document pages."""

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
        "document_id": document_id,
        "total_results": len(results),
        "search_method": "BM25",
        "results": results,
    }


@app.get("/clauses/search")
def search_clauses(
    q: str = Query(min_length=1),
    limit: int = Query(default=10, ge=1, le=50),
    document_id: str | None = None,
) -> dict:
    """Search individual TEC clauses."""

    query = q.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty.",
        )

    engine = get_search_engine()

    results = engine.search_clauses(
        query=query,
        limit=limit,
        document_id=document_id,
    )

    return {
        "query": query,
        "document_id": document_id,
        "total_results": len(results),
        "search_method": "BM25 clause-level",
        "results": results,
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
    """Answer questions using retrieved TEC clauses."""

    query = q.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    engine = get_search_engine()

    results = engine.search_clauses(
        query=query,
        limit=limit,
        document_id=document_id,
    )

    if not results:
        return {
            "question": query,
            "answer": "No relevant TEC document clauses were found.",
            "search_method": "BM25 clause-level",
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

        citations.append({
            "document_id": result["document_id"],
            "page_number": result["page_number"],
            "clause_number": result["clause_number"],
            "clause_title": result["clause_title"],
        })

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

            # Compatibility with older mocked functions.
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
            "from the TEC documents:\n\n"
            + "\n\n".join(context_parts)
        )

        answer_source = "tec_document_fallback"

    return {
        "question": query,
        "answer": answer,
        "search_method": "BM25 clause-level",
        "answer_source": answer_source,
        "citations": citations,
    }
