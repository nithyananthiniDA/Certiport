
import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi

DATA_DIR = Path("data/processed")
CLAUSE_FILE = DATA_DIR / "clauses.json"


def tokenize(text: str) -> list[str]:
    """Convert text into searchable tokens."""
    return re.findall(r"\d+(?:\.\d+)+|[a-zA-Z0-9]+", text.lower())


def normalize_document_id(document_id: str) -> str:
    """Normalize document IDs for comparison."""
    return re.sub(r"[^a-z0-9]", "", document_id.lower())


class TelecomSearch:
    def __init__(self):
        self.documents = []
        self.clauses = []

        # Load page-level JSON files.
        if DATA_DIR.exists():
            for file_path in DATA_DIR.glob("*.json"):
                if file_path.name == "clauses.json":
                    continue

                try:
                    with file_path.open("r", encoding="utf-8") as file:
                        data = json.load(file)

                    if isinstance(data, list):
                        self.documents.extend(data)

                except (json.JSONDecodeError, OSError) as error:
                    print(f"Could not load {file_path}: {error}")

        print(f"Loaded {len(self.documents)} pages.")

        self.page_tokens = [
            tokenize(
                f"{doc.get('document_id', '')} "
                f"{doc.get('page_number', '')} "
                f"{doc.get('text', '')}"
            )
            for doc in self.documents
        ]

        self.page_vocabulary = {
            token
            for document_tokens in self.page_tokens
            for token in document_tokens
        }

        self.page_bm25 = (
            BM25Okapi(self.page_tokens)
            if self.page_tokens
            else None
        )

        # Load clause-level JSON data.
        if CLAUSE_FILE.exists():
            try:
                with CLAUSE_FILE.open("r", encoding="utf-8") as file:
                    self.clauses = json.load(file)

            except (json.JSONDecodeError, OSError) as error:
                print(f"Could not load clauses: {error}")

        print(f"Loaded {len(self.clauses)} clauses.")

        self.clause_tokens = [
            tokenize(
                f"{clause.get('document_id', '')} "
                f"{clause.get('clause_number', '')} "
                f"{clause.get('clause_title', '')} "
                f"{clause.get('text', '')}"
            )
            for clause in self.clauses
        ]

        self.clause_vocabulary = {
            token
            for clause_tokens in self.clause_tokens
            for token in clause_tokens
        }

        self.clause_bm25 = (
            BM25Okapi(self.clause_tokens)
            if self.clause_tokens
            else None
        )

    def search(
        self,
        query: str,
        limit: int = 5,
        document_id: str | None = None,
    ) -> list[dict]:
        """Search TEC documents at page level."""

        tokens = tokenize(query)

        if not tokens or not self.documents or self.page_bm25 is None:
            return []

        # Reject the query if any token is unknown.
        if not all(
            token in self.page_vocabulary
            for token in tokens
        ):
            return []

        scores = self.page_bm25.get_scores(tokens)

        results = []

        for index, score in enumerate(scores):
            document = self.documents[index]

            if document_id:
                if normalize_document_id(
                    document.get("document_id", "")
                ) != normalize_document_id(document_id):
                    continue

            if score <= 0:
                continue

            results.append({
                "document_id": document.get("document_id"),
                "page_number": document.get("page_number"),
                "score": float(score),
                "matched_text": document.get("text", "")[:1000],
            })

        results.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return results[:limit]

    def search_clauses(
        self,
        query: str,
        limit: int = 5,
        document_id: str | None = None,
    ) -> list[dict]:
        """Search TEC documents at clause level."""

        query = query.strip()

        if not query or not self.clauses:
            return []

        # Filter by document ID when provided.
        filtered_clauses = self.clauses

        if document_id:
            normalized_id = normalize_document_id(document_id)

            filtered_clauses = [
                clause
                for clause in self.clauses
                if normalize_document_id(
                    clause.get("document_id", "")
                ) == normalized_id
            ]

        if not filtered_clauses:
            return []

        # Exact clause-number lookup.
        exact_matches = [
            clause
            for clause in filtered_clauses
            if clause.get("clause_number", "").strip() == query
        ]

        if exact_matches:
            return [
                {
                    "document_id": clause.get("document_id"),
                    "page_number": clause.get("page_number"),
                    "clause_number": clause.get("clause_number"),
                    "clause_title": clause.get("clause_title"),
                    "score": 1.0,
                    "matched_text": clause.get("text", "")[:1000],
                }
                for clause in exact_matches[:limit]
            ]

        query_tokens = tokenize(query)

        if not query_tokens:
            return []

        # Build BM25 for the filtered clauses.
        filtered_tokens = [
            tokenize(
                f"{clause.get('document_id', '')} "
                f"{clause.get('clause_number', '')} "
                f"{clause.get('clause_title', '')} "
                f"{clause.get('text', '')}"
            )
            for clause in filtered_clauses
        ]

        vocabulary = {
            token
            for clause_tokens in filtered_tokens
            for token in clause_tokens
        }

        # Reject queries containing unknown words.
        if not all(
            token in vocabulary
            for token in query_tokens
        ):
            return []

        bm25 = BM25Okapi(filtered_tokens)
        scores = bm25.get_scores(query_tokens)

        results = []

        for index, score in enumerate(scores):
            if score <= 0:
                continue

            clause = filtered_clauses[index]

            results.append({
                "document_id": clause.get("document_id"),
                "page_number": clause.get("page_number"),
                "clause_number": clause.get("clause_number"),
                "clause_title": clause.get("clause_title"),
                "score": float(score),
                "matched_text": clause.get("text", "")[:1000],
            })

        results.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return results[:limit]
