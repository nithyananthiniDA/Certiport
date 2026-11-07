from types import SimpleNamespace
from unittest.mock import MagicMock

from pydantic import SecretStr

import app.llm as llm


def test_generate_answer_without_api_charge(monkeypatch):
    fake_settings = SimpleNamespace(openai_api_key=SecretStr("test-api-key"))

    monkeypatch.setattr(
        llm,
        "get_settings",
        lambda: fake_settings,
    )

    mock_client = MagicMock()
    mock_client.responses.create.return_value.output_text = (
        "Clause 4.2.1 requires VRLA batteries to follow ISO 9001:2015 or its latest version."
    )

    monkeypatch.setattr(
        llm,
        "OpenAI",
        lambda **kwargs: mock_client,
    )

    answer = llm.generate_answer(
        "What is clause 4.2.1 about?",
        "Document: TEC 67010:2026. Page: 22. Clause: 4.2.1. VRLA batteries shall follow ISO 9001:2015.",
    )

    assert "VRLA batteries" in answer
    mock_client.responses.create.assert_called_once()
