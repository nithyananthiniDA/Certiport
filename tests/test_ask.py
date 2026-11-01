
from fastapi.testclient import TestClient

import app.main as main


class FakeSearchEngine:
    def search_clauses(self, query, limit, document_id):
        return [
            {
                "document_id": "TEC 67010:2026",
                "page_number": 22,
                "clause_number": "4.2.1",
                "clause_title": "VRLA Batteries",
                "matched_text": (
                    "VRLA batteries shall be manufactured "
                    "in accordance with ISO 9001:2015."
                ),
            }
        ]


def test_ask_returns_grounded_answer_without_api_charge(monkeypatch):
    monkeypatch.setattr(
        main,
        "get_search_engine",
        lambda: FakeSearchEngine(),
    )

    monkeypatch.setattr(
        main,
        "generate_answer",
        lambda question, context: (
            "Clause 4.2.1 requires VRLA batteries "
            "to follow ISO 9001:2015."
        ),
    )

    client = TestClient(main.app)

    response = client.get(
        "/ask",
        params={"q": "What is clause 4.2.1 about?"},
    )

    assert response.status_code == 200

    data = response.json()

    assert "VRLA batteries" in data["answer"]
    assert data["answer_source"] == "openai"
    assert data["citations"][0]["document_id"] == "TEC 67010:2026"
    assert data["citations"][0]["page_number"] == 22
    assert data["citations"][0]["clause_number"] == "4.2.1"


def test_ask_returns_tec_fallback_when_openai_fails(monkeypatch):
    monkeypatch.setattr(
        main,
        "get_search_engine",
        lambda: FakeSearchEngine(),
    )

    def fail_openai(question, context):
        raise ValueError("OpenAI API is unavailable.")

    monkeypatch.setattr(
        main,
        "generate_answer",
        fail_openai,
    )

    client = TestClient(main.app)

    response = client.get(
        "/ask",
        params={"q": "What is clause 4.2.1 about?"},
    )

    assert response.status_code == 200

    data = response.json()

    assert "ISO 9001:2015" in data["answer"]
    assert data["answer_source"] == "tec_document_fallback"
    assert data["citations"][0]["document_id"] == "TEC 67010:2026"
    assert data["citations"][0]["page_number"] == 22
    assert data["citations"][0]["clause_number"] == "4.2.1"
