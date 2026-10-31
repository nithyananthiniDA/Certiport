
from app.clause_extractor import extract_clauses


def test_extract_clauses():
    text = """
    1.1 Introduction
    This document describes the IoT Gateway.

    1.1.1 Scope
    This standard specifies requirements.

    1.1.2 Definitions
    An IoT Gateway connects devices.
    """

    clauses = extract_clauses(text)

    assert len(clauses) == 3
    assert clauses[0]["clause_number"] == "1.1"
    assert clauses[1]["clause_number"] == "1.1.1"
    assert clauses[2]["clause_number"] == "1.1.2"


def test_ignore_table_of_contents():
    text = """
    1.1 Introduction ........................................ 17
    1.2 Functions of IoT Gateway ............................ 17
    1.3 Description ........................................ 18
    1.9 Security Requirements .............................. 38
    """

    clauses = extract_clauses(text)

    assert clauses == []


def test_extract_clause_text():
    text = """
    1.1 Introduction
    This document describes the IoT Gateway.

    1.2 Functions
    The gateway supports device management.
    """

    clauses = extract_clauses(text)

    assert "Introduction" in clauses[0]["text"]
    assert "device management" in clauses[1]["text"]


def test_empty_text():
    clauses = extract_clauses("")

    assert clauses == []


def test_no_numbered_clauses():
    text = """
    This document describes telecom requirements.
    The gateway supports network connectivity.
    """

    clauses = extract_clauses(text)

    assert clauses == []
