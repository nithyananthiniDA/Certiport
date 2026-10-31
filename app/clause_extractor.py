
import re


def is_table_of_contents(text: str) -> bool:
    """Identify pages containing Table of Contents entries."""
    lines = text.splitlines()

    toc_lines = sum(
        1
        for line in lines
        if re.search(r"\.{3,}\s*\d+\s*$", line.strip())
    )

    return toc_lines >= 3


def extract_clauses(
    text: str,
    document_id: str = "",
    page_number: int = 0
) -> list[dict]:
    """
    Extract numbered clauses with document and page information.
    """

    if not text.strip() or is_table_of_contents(text):
        return []

    pattern = re.compile(
        r"(?m)^\s*(\d+(?:\.\d+)+)\.?\s+(.+?)\s*$"
    )

    matches = list(pattern.finditer(text))
    clauses = []

    for index, match in enumerate(matches):

        clause_number = match.group(1)
        clause_title = match.group(2).strip()

        start = match.start()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(text)

        clause_text = text[start:end].strip()

        if len(clause_text) < 10:
            continue

        if re.search(r"\.{3,}\s*\d+\s*$", clause_text):
            continue

        clauses.append({
            "document_id": document_id,
            "page_number": page_number,
            "clause_number": clause_number,
            "clause_title": clause_title,
            "text": clause_text
        })

    return clauses
