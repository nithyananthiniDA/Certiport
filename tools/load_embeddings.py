
import json
from pathlib import Path

from app.database import get_connection

EMBEDDINGS_FILE = Path("data/processed/embeddings.json")
BATCH_SIZE = 50


def load_embeddings():
    with EMBEDDINGS_FILE.open("r", encoding="utf-8") as file:
        records = json.load(file)

    print(f"Loaded {len(records)} embedding records.")

    insert_query = """
        INSERT INTO document_chunks
        (document_id, page_number, chunk_index, content, embedding)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (document_id, page_number, chunk_index)
        DO UPDATE SET
            content = EXCLUDED.content,
            embedding = EXCLUDED.embedding;
    """

    inserted = 0

    with get_connection() as conn:
        with conn.cursor() as cursor:
            for start in range(0, len(records), BATCH_SIZE):
                batch = records[start:start + BATCH_SIZE]

                values = [
                    (
                        item["document_id"],
                        item["page_number"],
                        item["chunk_index"],
                        item["text"],
                        item["embedding"],
                    )
                    for item in batch
                ]

                cursor.executemany(insert_query, values)
                inserted += len(batch)

                print(f"Processed {inserted}/{len(records)} records")

    print("\nEmbedding loading completed!")
    print(f"Total records processed: {inserted}")


if __name__ == "__main__":
    load_embeddings()
