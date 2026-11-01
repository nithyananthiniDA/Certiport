
from openai import OpenAI

from app.config import get_settings

MODEL_NAME = "gpt-4.1-mini"

# Estimated USD prices per 1 million tokens.
INPUT_PRICE_PER_MILLION = 0.40
OUTPUT_PRICE_PER_MILLION = 1.60

_usage = {
    "requests": 0,
    "input_tokens": 0,
    "output_tokens": 0,
    "total_tokens": 0,
    "estimated_cost_usd": 0.0,
}


def get_usage() -> dict:
    """Return accumulated LLM token usage and estimated cost."""
    return {
        **_usage,
        "estimated_cost_usd": round(
            _usage["estimated_cost_usd"], 8
        ),
        "model": MODEL_NAME,
    }


def generate_answer(question: str, context: str) -> str:
    """Generate an answer using retrieved TEC document content."""

    settings = get_settings()

    if not settings.openai_api_key:
        raise ValueError("OpenAI API key is not configured.")

    client = OpenAI(
        api_key=settings.openai_api_key.get_secret_value()
    )

    response = client.responses.create(
        model=MODEL_NAME,
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

    usage = response.usage

    if usage is not None:
        input_tokens = usage.input_tokens
        output_tokens = usage.output_tokens

        _usage["requests"] += 1
        _usage["input_tokens"] += input_tokens
        _usage["output_tokens"] += output_tokens
        _usage["total_tokens"] += input_tokens + output_tokens

        estimated_cost = (
            input_tokens * INPUT_PRICE_PER_MILLION
            + output_tokens * OUTPUT_PRICE_PER_MILLION
        ) / 1_000_000

        _usage["estimated_cost_usd"] += estimated_cost

    return response.output_text
