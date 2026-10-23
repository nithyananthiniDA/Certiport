
from pathlib import Path
import argparse
import json
from pypdf import PdfReader


def extract_pdf(pdf_path: Path, output_path: Path, document_id: str) -> None:
    """Extract PDF pages and save them as JSON records."""

    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        raise FileNotFoundError(f"PDF is missing or empty: {pdf_path}")

    print(f"Reading PDF: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        pages.append({
            "document_id": document_id,
            "page_number": page_number,
            "text": text
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(pages, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("PDF pages extracted:", len(pages))
    print("Saved JSON file:", output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Extract TEC PDF documents into JSON."
    )

    parser.add_argument(
        "--input",
        default="data/sample/TEC_67010_2026.pdf"
    )

    parser.add_argument(
        "--output",
        default="data/processed/tec_67010_2026.json"
    )

    parser.add_argument(
        "--document-id",
        default="TEC 67010:2026"
    )

    args = parser.parse_args()

    extract_pdf(
        Path(args.input),
        Path(args.output),
        args.document_id
    )


if __name__ == "__main__":
    main()
