import json
from pathlib import Path

from app.chunking import chunk_pages


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "data" / "chunks"
OUTPUT_FILE = OUTPUT_DIR / "chunks.json"


def main():
    all_pages = []

    for json_file in sorted(PROCESSED_DIR.glob("*.json")):
        if json_file.name == "clauses.json":
            continue

        with json_file.open("r", encoding="utf-8") as file:
            pages = json.load(file)

        if not isinstance(pages, list):
            print(f"Skipping unexpected format: {json_file.name}")
            continue

        all_pages.extend(pages)
        print(f"Loaded {len(pages)} pages: {json_file.name}")

    chunks = chunk_pages(all_pages, chunk_size=500, overlap=75)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(chunks, file, ensure_ascii=False, indent=2)

    print("\nDocument processing completed!")
    print("Total pages:", len(all_pages))
    print("Total chunks:", len(chunks))
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()