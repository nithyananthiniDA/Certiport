
import json
from pathlib import Path

from app.chunking import chunk_pages

DATA_DIR = Path("data/processed")
OUTPUT_FILE = DATA_DIR / "chunks.json"


def main():
    all_pages = []

    for file_path in DATA_DIR.glob("*.json"):
        if file_path.name in {"clauses.json", "chunks.json"}:
            continue

        with file_path.open("r", encoding="utf-8") as file:
            pages = json.load(file)

        if not isinstance(pages, list):
            print(f"Skipping unexpected format: {file_path.name}")
            continue

        all_pages.extend(pages)
        print(f"Loaded {len(pages)} pages from {file_path.name}")

    chunks = chunk_pages(all_pages, chunk_size=500, overlap=75)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(chunks, file, ensure_ascii=False, indent=2)

    print(f"\nTotal pages loaded: {len(all_pages)}")
    print(f"Total chunks created: {len(chunks)}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

