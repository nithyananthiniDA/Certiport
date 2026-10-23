
def test_search_clause_4_2_1(client):
    response = client.get("/search", params={"q": "4.2.1"})

    assert response.status_code == 200

    data = response.json()
    assert data["query"] == "4.2.1"
    assert data["total_results"] >= 1

    result = data["results"][0]
    assert result["document_id"] == "TEC 67010:2026"
    assert result["page_number"] == 22
    assert "ISO 9001:2015" in result["matched_text"]


def test_search_clause_5_1_1(client):
    response = client.get("/search", params={"q": "5.1.1"})

    assert response.status_code == 200

    data = response.json()
    assert data["total_results"] >= 1

    page_numbers = [
        result["page_number"]
        for result in data["results"]
    ]

    assert 25 in page_numbers


def test_search_unknown_keyword(client):
    response = client.get(
        "/search",
        params={"q": "zzzz_nonexistent_term_98765"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["total_results"] == 0
    assert data["results"] == []
