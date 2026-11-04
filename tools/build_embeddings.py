
import json
from pathlib import Path

from app.embeddings import generate_embeddings

CHUNKS_FILE = Path("data/processed/chunks.json")
OUTPUT_FILE = Path("data/processed/embeddings.json")
BATCH_SIZE = 16


def main():
    with CHUNKS_FILE.open("r", encoding="utf-8") as file:
        chunks = json.load(file)

    results = []

    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]
        texts = [chunk["text"] for chunk in batch]

        vectors = generate_embeddings(texts)

        for chunk, vector in zip(batch, vectors):
            results.append({
                **chunk,
                "embedding": vector
            })

        print(f"Processed {len(results)}/{len(chunks)} chunks")

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False)

    print("\nEmbedding generation completed!")
    print(f"Total embeddings: {len(results)}")
    print(f"Vector dimensions: {len(results[0]['embedding'])}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
