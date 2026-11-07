import json
from urllib.request import Request, urlopen

from app.config import get_settings

EMBEDDING_MODEL = "nomic-embed-text"


def generate_embeddings(texts):
    """Generate embeddings for a list of texts using local Ollama."""

    if not texts:
        return []

    settings = get_settings()
    ollama_url = settings.ollama_base_url.rstrip("/") + "/api/embed"

    payload = {"model": EMBEDDING_MODEL, "input": texts}

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    request = Request(
        ollama_url, data=body, headers={"Content-Type": "application/json; charset=utf-8"}, method="POST"
    )

    with urlopen(request, timeout=120) as response:
        result = json.loads(response.read().decode("utf-8"))

    embeddings = result["embeddings"]

    if len(embeddings) != len(texts):
        raise ValueError("Embedding count does not match input count")

    if any(len(vector) != 768 for vector in embeddings):
        raise ValueError("Unexpected embedding dimension")

    return embeddings
