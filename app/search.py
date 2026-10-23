
import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi


DATA_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "processed"
)


def tokenize(text: str) -> list[str]:
    """Convert text into lowercase words and clause numbers."""
    return re.findall(r"\d+(?:\.\d+)+|[a-zA-Z0-9]+", text.lower())


class TelecomSearch:
    """Search TEC document pages using BM25 ranking."""

    def __init__(self) -> None:
        data_files = sorted(DATA_DIR.glob("*.json"))

        if not data_files:
            raise FileNotFoundError(
                f"No processed TEC JSON files found in: {DATA_DIR}"
            )

        self.pages = []

        # Load pages from every processed JSON document.
        for data_file in data_files:
            with data_file.open("r", encoding="utf-8") as file:
                document_pages = json.load(file)

            if not isinstance(document_pages, list):
                raise ValueError(
                    f"Expected a list of pages in: {data_file}"
                )

            self.pages.extend(document_pages)

        if not self.pages:
            raise ValueError("No document pages were loaded.")

        print(
            f"Loaded {len(self.pages)} pages "
            f"from {len(data_files)} JSON files."
        )

        # Tokenize every page from all documents.
        self.tokens = [
            tokenize(page.get("text", ""))
            for page in self.pages
        ]

        # Create one BM25 ranking engine for all pages.
        self.bm25 = BM25Okapi(self.tokens)

        # Store all words found in the document collection.
        self.corpus_terms = {
            token
            for page_tokens in self.tokens
            for token in page_tokens
        }

    def search(self, query: str, limit: int = 10) -> list[dict]:
        """Return relevant TEC pages ranked by BM25."""

        query = query.strip()

        if not query or limit <= 0:
            return []

        # Treat underscore-connected queries as complete identifiers.
        if "_" in query:
            query_in_corpus = any(
                query.lower() in page.get("text", "").lower()
                for page in self.pages
            )

            if not query_in_corpus:
                return []

        query_tokens = tokenize(query)

        if not query_tokens:
            return []

        # Search exact clause numbers, such as 4.2.1.
        if re.fullmatch(r"\d+(?:\.\d+)+", query):
            pattern = re.compile(
                rf"(?<![\w.]){re.escape(query)}(?![\w.])",
                re.IGNORECASE,
            )

            matching_indices = [
                index
                for index, page in enumerate(self.pages)
                if pattern.search(page.get("text", ""))
            ]

            scores = self.bm25.get_scores(query_tokens)

            matching_indices.sort(
                key=lambda index: float(scores[index]),
                reverse=True,
            )

            ranked_indices = matching_indices

        else:
            # Ignore words that do not exist in the document collection.
            valid_terms = {
                token
                for token in query_tokens
                if not token.isdigit()
                and token in self.corpus_terms
            }

            if not valid_terms:
                return []

            scores = self.bm25.get_scores(query_tokens)

            # Keep pages containing at least one known query word.
            ranked_indices = [
                index
                for index, page_tokens in enumerate(self.tokens)
                if valid_terms.intersection(page_tokens)
            ]

            ranked_indices.sort(
                key=lambda index: float(scores[index]),
                reverse=True,
            )

        results = []

        for index in ranked_indices[:limit]:
            page = self.pages[index]
            page_text = page.get("text", "")
            lower_text = page_text.lower()

            # Find the matching clause or keyword in the page.
            if re.fullmatch(r"\d+(?:\.\d+)+", query):
                match = re.search(
                    rf"(?<![\w.]){re.escape(query)}(?![\w.])",
                    page_text,
                    re.IGNORECASE,
                )

                position = match.start() if match else 0

            else:
                positions = [
                    lower_text.find(term)
                    for term in valid_terms
                    if lower_text.find(term) >= 0
                ]

                position = min(positions) if positions else 0

            # Return a short excerpt around the match.
            start = max(0, position - 250)
            end = min(len(page_text), position + len(query) + 350)

            results.append(
                {
                    "document_id": page.get("document_id"),
                    "page_number": page.get("page_number"),
                    "score": round(float(scores[index]), 4),
                    "matched_text": page_text[start:end].strip(),
                }
            )

        return results
