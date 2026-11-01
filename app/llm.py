
from openai import OpenAI

from app.config import get_settings


def generate_answer(question: str, context: str) -> str:
    """Generate an answer using retrieved TEC document content."""

    settings = get_settings()

    if not settings.openai_api_key:
        raise ValueError("OpenAI API key is not configured.")

    client = OpenAI(
        api_key=settings.openai_api_key.get_secret_value()
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=(
            "You are CertiPort, a telecom certification assistant. "
            "Answer questions using only the supplied TEC document context. "
            "Do not invent technical requirements. "
            "If the context does not contain the answer, say so. "
            "Include document IDs, page numbers and clause numbers "
            "when available."
        ),
        input=(
            f"Question:\n{question}\n\n"
            f"TEC Document Context:\n{context}"
        ),
    )

    return response.output_text
