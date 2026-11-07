import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from openai import OpenAI, OpenAIError

from app.config import get_settings

OPENAI_MODEL = "gpt-4.1-mini"

INPUT_PRICE_PER_MILLION = 0.40
OUTPUT_PRICE_PER_MILLION = 1.60


SYSTEM_INSTRUCTIONS = """
You are CertiPort, a telecom certification assistant.

STRICT ANSWERING RULES:

1. Answer using only the supplied TEC document context.
2. Never invent technical requirements, test names, values, or procedures.
3. Read every relevant retrieved clause before preparing the answer.
4. If the question asks for multiple categories, create a separate
   heading for every requested category.
5. Never silently omit a category when its information is present
   in the supplied context.
6. Preserve technical test names exactly as written in the TEC document.
7. Include all relevant test entries found in the supplied context.
8. For test tables, preserve available Yes, No, and Verification
   values accurately.
9. Do not interpret a Yes or No value without understanding its
   corresponding table column.
10. If table formatting is ambiguous or column alignment is unclear,
    explicitly mention that acceptance-stage mapping needs verification
    from the original table.
11. Do not say that a test is not required merely because a table
    contains the word No.
12. Include document ID, page number, and clause number when available.
13. Do not confuse a clause heading with detailed test information
    in its subsections.
14. If the question asks for physical, electrical, chemical, or
    quality tests, include every relevant category available in context.

Before finishing, verify that every requested category and every
relevant test name in the supplied context has been addressed.
"""


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
        "estimated_cost_usd": round(_usage["estimated_cost_usd"], 8),
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

    if not context or not context.strip():
        raise ValueError("TEC document context cannot be empty.")

    # --------------------------------------------------
    # 1. Try OpenAI
    # --------------------------------------------------

    if settings.openai_api_key:
        try:
            client = OpenAI(
                api_key=settings.openai_api_key.get_secret_value(),
                timeout=30.0,
            )

            response = client.responses.create(
                model=OPENAI_MODEL,
                instructions=SYSTEM_INSTRUCTIONS,
                input=(
                    f"Question:\n{question}\n\n"
                    f"TEC Document Context:\n{context}\n\n"
                    "Prepare a complete and structured answer. "
                    "Cover every requested category. "
                    "Include every relevant test entry."
                ),
            )

            answer = response.output_text.strip()

            if not answer:
                raise ValueError("OpenAI returned an empty answer.")

            usage = response.usage

            if usage is not None:
                input_tokens = usage.input_tokens
                output_tokens = usage.output_tokens

                _usage["requests"] += 1
                _usage["input_tokens"] += input_tokens
                _usage["output_tokens"] += output_tokens
                _usage["total_tokens"] += input_tokens + output_tokens

                estimated_cost = (
                    input_tokens * INPUT_PRICE_PER_MILLION + output_tokens * OUTPUT_PRICE_PER_MILLION
                ) / 1_000_000

                _usage["estimated_cost_usd"] += estimated_cost

            _provider_usage["openai_requests"] += 1
            _last_used_model = OPENAI_MODEL

            if return_provider:
                return answer, "openai"

            return answer

        except (OpenAIError, ValueError):
            # If OpenAI fails, continue with Ollama.
            pass

    # --------------------------------------------------
    # 2. Ollama fallback
    # --------------------------------------------------

    url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"

    prompt = (
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        f"Question:\n{question}\n\n"
        f"TEC Document Context:\n{context}\n\n"
        "Prepare a complete, structured answer. "
        "Cover every requested category. "
        "Preserve test names and table information accurately. "
        "Do not omit relevant entries."
    )

    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 2048,
            "temperature": 0.1,
            "top_p": 0.9,
        },
    }

    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))

        answer = result.get("response", "").strip()

        if not answer:
            raise ValueError("Ollama returned an empty answer.")

        # Ollama token usage.
        input_tokens = result.get("prompt_eval_count") or 0
        output_tokens = result.get("eval_count") or 0

        _provider_usage["ollama_requests"] += 1

        _provider_usage["ollama_input_tokens"] += input_tokens

        _provider_usage["ollama_output_tokens"] += output_tokens

        _provider_usage["ollama_total_tokens"] += input_tokens + output_tokens

        _last_used_model = settings.ollama_model

        if return_provider:
            return answer, "ollama"

        return answer

    except (URLError, TimeoutError, OSError, ValueError) as exc:
        raise ValueError("Both OpenAI and local Ollama are unavailable.") from exc
