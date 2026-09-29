"""
API test suite for GeneMindAI FastAPI backend.

Tests health check endpoint, valid sequence predictions, error responses
for invalid characters/empty strings, edge cases for short, long, lowercase,
and whitespace-padded DNA sequences.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.main import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """
    Pytest fixture supplying a FastAPI TestClient instance within app lifespan context.
    """
    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client: TestClient) -> None:
    """Verify GET / health check endpoint returns 200 OK and expected status message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "GeneMindAI API Running"}


def test_valid_dna_sequence_prediction(client: TestClient) -> None:
    """Verify POST /predict with a valid DNA sequence returns 200 with prediction & valid confidence."""
    valid_sequence = (
        "ACATTTGCTTCTGACACAACTGTGTTCACTAGCAACCTCAAACAGACACCATGGTGCAT"
    )
    response = client.post("/predict", json={"sequence": valid_sequence})

    assert response.status_code == 200
    data = response.json()

    assert "prediction" in data
    assert isinstance(data["prediction"], str)
    assert len(data["prediction"]) > 0

    assert "confidence" in data
    assert isinstance(data["confidence"], (int, float))
    assert 0.0 <= data["confidence"] <= 1.0


def test_invalid_characters_dna_sequence(client: TestClient) -> None:
    """Verify POST /predict with invalid characters returns 400 Bad Request."""
    invalid_sequence = "ATGC123XYZ"
    response = client.post("/predict", json={"sequence": invalid_sequence})

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert (
        "Invalid DNA sequence" in data["detail"]
        or "invalid characters" in data["detail"].lower()
    )


def test_empty_dna_sequence(client: TestClient) -> None:
    """Verify POST /predict with empty sequence returns 400 Bad Request."""
    empty_sequence = ""
    response = client.post("/predict", json={"sequence": empty_sequence})

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_very_short_dna_sequence(client: TestClient) -> None:
    """Verify POST /predict with a very short valid DNA sequence responds gracefully without crashing."""
    short_sequence = "ATG"
    response = client.post("/predict", json={"sequence": short_sequence})

    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "confidence" in data
    assert 0.0 <= data["confidence"] <= 1.0


def test_long_dna_sequence(client: TestClient) -> None:
    """Verify POST /predict with a long DNA sequence (>= 10,000 bases) completes successfully."""
    long_sequence = "ATCG" * 2500  # 10,000 bases
    response = client.post("/predict", json={"sequence": long_sequence})

    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "confidence" in data
    assert 0.0 <= data["confidence"] <= 1.0


def test_lowercase_dna_sequence(client: TestClient) -> None:
    """Verify POST /predict with lowercase DNA input is accepted and processed correctly."""
    lowercase_sequence = (
        "acatttgcttctgacacaactgtgttcactagcaacctcaaacagacaccatggtgcat"
    )
    response = client.post("/predict", json={"sequence": lowercase_sequence})

    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "confidence" in data
    assert 0.0 <= data["confidence"] <= 1.0


def test_sequence_with_whitespace(client: TestClient) -> None:
    """Verify POST /predict with spaces and newlines is preprocessed correctly."""
    whitespace_sequence = (
        "  ACAT TTGC\n TTCT GACA CAAC TGTG\nTTCA CTAG CAAC CTC  "
    )
    response = client.post("/predict", json={"sequence": whitespace_sequence})

    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "confidence" in data
    assert 0.0 <= data["confidence"] <= 1.0
