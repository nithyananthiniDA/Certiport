
import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi


DATA_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "processed"
)

CLAUSE_FILE = DATA_DIR / "clauses.json"


def tokenize(text: str) -> list[str]:
    """Convert text into lowercase words and clause numbers."""
    return re.findall(
        r"\d+(?:\.\d+)+|[a-zA-Z0-9]+",
        text.lower()
    )


class TelecomSearch:
    """Search TEC document pages using BM25 ranking."""

    def __init__(self) -> None:

        # Load original page-level JSON files only.
        data_files = sorted(
            path
            for path in DATA_DIR.glob("*.json")
            if path.name != "clauses.json"
        )

        if not data_files:
            raise FileNotFoundError(
                f"No processed TEC JSON files found in: {DATA_DIR}"
            )

        self.pages = []

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

        # Build page-level BM25 index.
        self.tokens = [
            tokenize(page.get("text", ""))
            for page in self.pages
        ]

        self.bm25 = BM25Okapi(self.tokens)

    def search(
        self,
        query: str,
        limit: int = 10,
        document_id: str | None = None,
    ) -> list[dict]:
        """Search all documents or filter by a specific document ID."""

        query = query.strip()

        if not query or limit <= 0:
            return []

        # Filter pages by document ID when provided.
        if document_id:
            document_id = document_id.strip().casefold()

            candidate_indices = [
                index
                for index, page in enumerate(self.pages)
                if str(page.get("document_id", "")).strip().casefold()
                == document_id
            ]

            if not candidate_indices:
                return []
        else:
            candidate_indices = list(range(len(self.pages)))

        # Search by exact document ID.
        document_id_matches = [
            index
            for index in candidate_indices
            if str(self.pages[index].get("document_id", "")).strip().casefold()
            == query.casefold()
        ]

        if document_id_matches:
            return [
                {
                    "document_id": self.pages[index].get("document_id"),
                    "page_number": self.pages[index].get("page_number"),
                    "score": 1.0,
                    "matched_text": self.pages[index].get("text", "")[:600].strip(),
                }
                for index in document_id_matches[:limit]
            ]

        query_tokens = tokenize(query)

        if not query_tokens:
            return []

        # Search exact clause numbers.
        if re.fullmatch(r"\d+(?:\.\d+)+", query):

            pattern = re.compile(
                rf"(?<![\w.]){re.escape(query)}(?![\w.])",
                re.IGNORECASE,
            )

            ranked_indices = [
                index
                for index in candidate_indices
                if pattern.search(
                    self.pages[index].get("text", "")
                )
            ]

            if not ranked_indices:
                return []

            scores = self.bm25.get_scores(query_tokens)

            ranked_indices.sort(
                key=lambda index: float(scores[index]),
                reverse=True,
            )

        else:
            # Search keywords within the selected document collection.
            meaningful_terms = {
                token
                for token in query_tokens
                if not token.isdigit()
            }

            available_terms = {
                token
                for index in candidate_indices
                for token in self.tokens[index]
            }

            valid_terms = meaningful_terms.intersection(
                available_terms
            )

            # Reject queries containing unknown words.
            if (
                not meaningful_terms
                or not meaningful_terms.issubset(valid_terms)
            ):
                return []

            scores = self.bm25.get_scores(query_tokens)

            ranked_indices = [
                index
                for index in candidate_indices
                if valid_terms.intersection(self.tokens[index])
            ]

            ranked_indices.sort(
                key=lambda index: float(scores[index]),
                reverse=True,
            )

        # Prepare search results.
        results = []

        for index in ranked_indices[:limit]:

            page = self.pages[index]
            page_text = page.get("text", "")
            lower_text = page_text.lower()

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

            start = max(0, position - 250)
            end = min(
                len(page_text),
                position + len(query) + 350
            )

            results.append(
                {
                    "document_id": page.get("document_id"),
                    "page_number": page.get("page_number"),
                    "score": round(
                        float(scores[index]),
                        4
                    ),
                    "matched_text": page_text[start:end].strip(),
                }
            )

        return results
