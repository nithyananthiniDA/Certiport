
import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from openai import OpenAI, OpenAIError

from app.config import get_settings

OPENAI_MODEL = "gpt-4.1-mini"

INPUT_PRICE_PER_MILLION = 0.40
OUTPUT_PRICE_PER_MILLION = 1.60

_usage = {
    "requests": 0,
    "input_tokens": 0,
    "output_tokens": 0,
    "total_tokens": 0,
    "estimated_cost_usd": 0.0,
}

_provider_usage = {
    "openai_requests": 0,
    "ollama_requests": 0,
    "ollama_input_tokens": 0,
    "ollama_output_tokens": 0,
    "ollama_total_tokens": 0,
}

_last_used_model = None


def get_usage() -> dict:
    """Return accumulated LLM usage and estimated cost."""

    settings = get_settings()

    return {
        **_usage,
        **_provider_usage,
        "estimated_cost_usd": round(
            _usage["estimated_cost_usd"], 8
        ),
        "model": _last_used_model or OPENAI_MODEL,
        "ollama_model": settings.ollama_model,
    }


def generate_answer(
    question: str,
    context: str,
    return_provider: bool = False,
) -> str | tuple[str, str]:
    """Try OpenAI first, then local Ollama."""

    global _last_used_model

    settings = get_settings()

    if settings.openai_api_key:
        try:
            client = OpenAI(
                api_key=settings.openai_api_key.get_secret_value(),
                timeout=20.0,
            )

            response = client.responses.create(
                model=OPENAI_MODEL,
                instructions=(
                    "You are CertiPort, a telecom certification assistant. "
                    "Answer using only the supplied TEC document context. "
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
                _usage["total_tokens"] += (
                    input_tokens + output_tokens
                )

                estimated_cost = (
                    input_tokens * INPUT_PRICE_PER_MILLION
                    + output_tokens * OUTPUT_PRICE_PER_MILLION
                ) / 1_000_000

                _usage["estimated_cost_usd"] += estimated_cost

            _provider_usage["openai_requests"] += 1
            _last_used_model = OPENAI_MODEL

            if return_provider:
                return response.output_text, "openai"

            return response.output_text

        except (OpenAIError, ValueError):
            pass

    # Local Ollama fallback.
    url = (
        f"{settings.ollama_base_url.rstrip('/')}/api/generate"
    )

    prompt = (
        "You are CertiPort, a telecom certification assistant. "
        "Answer using only the supplied TEC document context. "
        "Do not invent technical requirements. "
        "If the context does not contain the answer, say so. "
        "Include document IDs, page numbers and clause numbers "
        "when available.\n\n"
        f"Question:\n{question}\n\n"
        f"TEC Document Context:\n{context}"
    )

    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
    }

    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=90) as response:
            result = json.loads(response.read().decode("utf-8"))

        answer = result.get("response", "").strip()

        if not answer:
            raise ValueError("Ollama returned an empty answer.")

        input_tokens = result.get("prompt_eval_count") or 0
        output_tokens = result.get("eval_count") or 0

        _provider_usage["ollama_requests"] += 1
        _provider_usage["ollama_input_tokens"] += input_tokens
        _provider_usage["ollama_output_tokens"] += output_tokens
        _provider_usage["ollama_total_tokens"] += (
            input_tokens + output_tokens
        )

        _last_used_model = settings.ollama_model

        if return_provider:
            return answer, "ollama"

        return answer

    except (URLError, TimeoutError, OSError, ValueError) as exc:
        raise ValueError(
            "Both OpenAI and local Ollama are unavailable."
        ) from exc
