from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """Request model for telecom certification questions."""

    question: str = Field(
        ...,
        min_length=1,
        description="Telecom certification question",
    )

    limit: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of retrieved clauses",
    )

    document_id: str | None = Field(
        default=None,
        description="Optional TEC document identifier",
    )


class Citation(BaseModel):
    """Citation from a TEC document."""

    document_id: str
    page_number: int
    clause_number: str
    clause_title: str


class AskResponse(BaseModel):
    """Structured response for telecom certification questions."""

    question: str
    answer: str
    search_method: str
    answer_source: str
    citations: list[Citation]
