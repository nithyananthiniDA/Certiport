
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query

from app.config import Settings, get_settings
from app.search import TelecomSearch

app = FastAPI(
    title="CertiPort Telecom Search",
    description="Search official TEC telecom standards and MTCTE documents.",
    version="0.4.0",
)

SettingsDep = Annotated[Settings, Depends(get_settings)]

_search_engine: TelecomSearch | None = None


def get_search_engine() -> TelecomSearch:
    """Load the search engine when needed."""
    global _search_engine

    if _search_engine is None:
        try:
            _search_engine = TelecomSearch()

        except FileNotFoundError:
            raise HTTPException(
                status_code=503,
                detail="TEC document data is not available.",
            )

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


@app.get("/search")
def search_document(
    q: str = Query(
        min_length=1,
        description="Search for a TEC clause, document ID, or keyword.",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of results.",
    ),
    document_id: str | None = Query(
        default=None,
        description="Optional TEC document ID filter.",
    ),
) -> dict:
    """Search TEC pages using BM25 ranking."""

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
        "limit": limit,
        "results": results,
    }
