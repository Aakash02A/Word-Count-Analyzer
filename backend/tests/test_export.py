import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.export_service import export_service
from app.schemas.analysis import AnalysisResponse, AnalysisMetadata, WordFrequencyItem, BigramItem, WordLengthItem, SentimentResult

client = TestClient(app)


def test_sanitize_cell_formula_injection():
    # Formula prefixes: =, +, -, @, \t, \r
    assert export_service.sanitize_cell("=SUM(A1:A10)") == "'=SUM(A1:A10)"
    assert export_service.sanitize_cell("+cmd|' /C calc'!A0") == "'+cmd|' /C calc'!A0"
    assert export_service.sanitize_cell("-2+3") == "'-2+3"
    assert export_service.sanitize_cell("@SUM(1,2)") == "'@SUM(1,2)"
    assert export_service.sanitize_cell("normal_word") == "normal_word"


def test_generate_analysis_csv():
    freqs = [
        WordFrequencyItem(word="hello", count=2, percentage=50.0),
        WordFrequencyItem(word="=malicious", count=1, percentage=25.0),
        WordFrequencyItem(word="world", count=1, percentage=25.0),
    ]
    payload = AnalysisResponse(
        total_tokens=4,
        unique_tokens=3,
        average_word_length=4.5,
        top_words=freqs,
        word_frequencies=freqs,
        bigrams=[
            BigramItem(bigram="hello world", count=1),
        ],
        word_length_distribution=[
            WordLengthItem(length=5, count=3),
        ],
        sentiment=SentimentResult(
            polarity=0.5,
            subjectivity=0.6,
            label="positive",
        ),
        noun_phrases=["hello world"],
        metadata=AnalysisMetadata(
            source_type="raw_text",
            source_name="Sample",
            raw_character_count=20,
            normalized_character_count=20,
            case_sensitive=False,
            top_n_requested=10,
            engine_used="python_in_memory",
            execution_time_ms=1.2,
        ),
    )

    csv_text = export_service.generate_analysis_csv(payload)
    assert "# WORD INTELLIGENCE ANALYSIS REPORT" in csv_text
    assert "'=malicious" in csv_text
    assert "hello" in csv_text
    assert "positive" in csv_text
    assert "# FREQUENT BIGRAMS" in csv_text
    assert "hello world" in csv_text


def test_export_endpoint():
    freqs = [
        {"word": "data", "count": 1, "percentage": 50.0},
        {"word": "test", "count": 1, "percentage": 50.0},
    ]
    request_data = {
        "total_tokens": 2,
        "unique_tokens": 2,
        "average_word_length": 4.0,
        "top_words": freqs,
        "word_frequencies": freqs,
        "bigrams": [
            {"bigram": "data test", "count": 1}
        ],
        "word_length_distribution": [
            {"length": 4, "count": 2}
        ],
        "noun_phrases": ["data test"],
        "metadata": {
            "source_type": "raw_text",
            "source_name": "Test Input",
            "raw_character_count": 9,
            "normalized_character_count": 9,
            "case_sensitive": False,
            "top_n_requested": 10,
            "engine_used": "python_in_memory",
            "execution_time_ms": 0.5,
        }
    }
    response = client.post("/api/v1/export/csv", json=request_data)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment; filename=" in response.headers["content-disposition"]
    assert "data" in response.text
    assert "test" in response.text
