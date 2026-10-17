import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.services.analyzer import TextAnalyzer
from app.services.preprocessor import TextPreprocessor


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


# ==============================================================================
# Unit Tests: Preprocessor & Tokenizer
# ==============================================================================

def test_preprocessor_whitespace_normalization():
    raw = "  Hello   \n\n\t world!  This   is    spaced.   "
    normalized = TextPreprocessor.normalize_text(raw)
    assert normalized == "Hello world! This is spaced."


def test_preprocessor_tokenization_basic():
    text = "Java is powerful and Java is popular."
    tokens = TextPreprocessor.tokenize(text, case_sensitive=False)
    assert tokens == ["java", "is", "powerful", "and", "java", "is", "popular"]


def test_preprocessor_tokenization_case_sensitive():
    text = "Java java JAVA"
    tokens = TextPreprocessor.tokenize(text, case_sensitive=True)
    assert tokens == ["Java", "java", "JAVA"]


def test_preprocessor_punctuation_and_hyphenation():
    text = "It's a state-of-the-art solution, isn't it?"
    tokens = TextPreprocessor.tokenize(text, case_sensitive=False)
    assert "it's" in tokens
    assert "state-of-the-art" in tokens
    assert "isn't" in tokens


def test_preprocessor_unicode_handling():
    text = "Un café délicieux et un résumé parfait."
    tokens = TextPreprocessor.tokenize(text, case_sensitive=False)
    assert "café" in tokens
    assert "délicieux" in tokens
    assert "résumé" in tokens


# ==============================================================================
# Unit Tests: Text Analyzer
# ==============================================================================

def test_analyzer_deterministic_output():
    text = "Java is powerful and Java is popular."
    res = TextAnalyzer.analyze(text=text, top_n=10, case_sensitive=False)

    assert res.total_tokens == 7
    assert res.unique_tokens == 5
    # Tied counts (is: 2, java: 2) should be ordered alphabetically: 'is' then 'java'
    assert res.top_words[0].word == "is"
    assert res.top_words[0].count == 2
    assert res.top_words[1].word == "java"
    assert res.top_words[1].count == 2
    assert res.top_words[0].percentage == 28.57

    # Bigrams: "java is" appears 2 times
    assert len(res.bigrams) > 0
    assert res.bigrams[0].bigram == "java is"
    assert res.bigrams[0].count == 2


def test_analyzer_single_word():
    text = "Antigravity"
    res = TextAnalyzer.analyze(text=text, top_n=5)
    assert res.total_tokens == 1
    assert res.unique_tokens == 1
    assert res.average_word_length == 11.0
    assert len(res.bigrams) == 0
    assert len(res.word_length_distribution) == 1
    assert res.word_length_distribution[0].length == 11
    assert res.word_length_distribution[0].count == 1


def test_analyzer_word_length_distribution():
    text = "a bb ccc dddd e"
    res = TextAnalyzer.analyze(text=text)
    assert res.total_tokens == 5
    assert res.unique_tokens == 5
    # Lengths: 1: 2 (a, e), 2: 1 (bb), 3: 1 (ccc), 4: 1 (dddd)
    lengths = {item.length: item.count for item in res.word_length_distribution}
    assert lengths[1] == 2
    assert lengths[2] == 1
    assert lengths[3] == 1
    assert lengths[4] == 1


# ==============================================================================
# API Integration Tests: POST /api/v1/analysis
# ==============================================================================

def test_api_analysis_success(client: TestClient):
    payload = {
        "text": "Data analytics and big data processing with Python.",
        "top_n": 5,
        "case_sensitive": False,
    }
    response = client.post("/api/v1/analysis", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_tokens"] == 8
    assert data["unique_tokens"] == 7  # 'data' appears twice
    assert data["top_words"][0]["word"] == "data"
    assert data["top_words"][0]["count"] == 2
    assert len(data["top_words"]) <= 5
    assert len(data["word_length_distribution"]) > 0
    assert data["metadata"]["raw_character_count"] == len(payload["text"])


def test_api_analysis_case_sensitive(client: TestClient):
    payload = {
        "text": "Apple apple APPLE",
        "case_sensitive": True,
    }
    response = client.post("/api/v1/analysis", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_tokens"] == 3
    assert data["unique_tokens"] == 3


def test_api_analysis_empty_text_error(client: TestClient):
    response = client.post("/api/v1/analysis", json={"text": ""})
    assert response.status_code == 422


def test_api_analysis_whitespace_only_error(client: TestClient):
    response = client.post("/api/v1/analysis", json={"text": "   \n\t   "})
    assert response.status_code == 422
    assert "whitespace-only" in response.json()["detail"]


def test_api_analysis_invalid_top_n(client: TestClient):
    response = client.post("/api/v1/analysis", json={"text": "Hello world", "top_n": 0})
    assert response.status_code == 422


def test_api_analysis_oversized_payload(client: TestClient, monkeypatch):
    monkeypatch.setattr(settings, "MAX_TEXT_LENGTH_CHARS", 50)
    oversized = "a" * 100
    response = client.post("/api/v1/analysis", json={"text": oversized})
    assert response.status_code == 413
    assert "exceeds maximum allowed size" in response.json()["detail"]
