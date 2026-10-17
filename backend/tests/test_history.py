import pytest
from starlette.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal, check_db_connectivity
from app.services.history_service import history_service
from app.schemas.analysis import (
    AnalysisMetadata,
    AnalysisResponse,
    SentimentResult,
    WordFrequencyItem,
    WordLengthItem,
    BigramItem,
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_database_connectivity_probe():
    """Verify check_db_connectivity returns successful connection and non-zero latency."""
    status = check_db_connectivity()
    assert status["connected"] is True
    assert status["database"] == "word_intelligence"
    assert status["latency_ms"] is not None
    assert status["latency_ms"] >= 0


def test_readiness_endpoint(client: TestClient):
    """Verify /api/v1/readiness returns ready status and dependency health metadata."""
    response = client.get("/api/v1/readiness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"]["connected"] is True
    assert "spark" in data


def test_history_crud_service(db_session):
    """Verify HistoryService persistence, retrieval, listing, and deletion."""
    mock_response = AnalysisResponse(
        total_tokens=25,
        unique_tokens=18,
        average_word_length=4.8,
        top_words=[
            WordFrequencyItem(word="spark", count=3, percentage=12.0),
            WordFrequencyItem(word="python", count=2, percentage=8.0),
        ],
        word_frequencies=[
            WordFrequencyItem(word="spark", count=3, percentage=12.0),
            WordFrequencyItem(word="python", count=2, percentage=8.0),
        ],
        word_length_distribution=[
            WordLengthItem(length=5, count=10),
            WordLengthItem(length=6, count=8),
        ],
        bigrams=[
            BigramItem(bigram="spark python", count=2),
        ],
        sentiment=SentimentResult(
            polarity=0.35,
            subjectivity=0.45,
            label="positive",
        ),
        noun_phrases=["apache pyspark", "distributed dataframe"],
        metadata=AnalysisMetadata(
            raw_character_count=120,
            normalized_character_count=115,
            case_sensitive=False,
            top_n_requested=10,
            engine_used="python",
            source_type="text",
            source_name="PyTest Unit Run",
            execution_time_ms=12.5,
        ),
    )

    # 1. Save
    record = history_service.save_analysis(
        db=db_session,
        response=mock_response,
        source_type="text",
        source_name="PyTest Unit Run",
        engine="python",
        case_sensitive=False,
        top_n=10,
        processing_time_ms=12,
    )
    assert record.id is not None
    assert record.total_words == 25
    assert record.sentiment_label == "positive"

    # 2. Retrieve by ID
    fetched = history_service.get_history_by_id(db_session, record.id)
    assert fetched is not None
    assert fetched.source_name == "PyTest Unit Run"
    parsed_payload = fetched.get_parsed_result()
    assert parsed_payload["total_tokens"] == 25
    assert len(parsed_payload["top_words"]) == 2

    # 3. List
    records, total = history_service.list_history(db_session, search="PyTest Unit Run")
    assert total >= 1
    assert any(r.id == record.id for r in records)

    # 4. Stats
    stats = history_service.get_stats(db_session)
    assert stats["total_runs"] >= 1
    assert stats["total_words_analyzed"] >= 25

    # 5. Delete
    deleted = history_service.delete_history(db_session, record.id)
    assert deleted is True
    assert history_service.get_history_by_id(db_session, record.id) is None


def test_api_history_endpoints(client: TestClient):
    """Verify REST API /api/v1/history endpoints including auto-persistence on analysis."""
    # 1. Trigger an analysis to auto-persist a record
    unique_keyword = "AutomatedTestRunKeyword"
    analyze_res = client.post(
        "/api/v1/analysis",
        json={"text": f"This is an {unique_keyword} verifying history database persistence with python engine.", "top_n": 5},
    )
    assert analyze_res.status_code == 200

    # 2. Query history list
    list_res = client.get("/api/v1/history?limit=10")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert "items" in list_data
    assert list_data["total"] >= 1
    latest_item = list_data["items"][0]
    record_id = latest_item["id"]

    # 3. Query history detail
    detail_res = client.get(f"/api/v1/history/{record_id}")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["id"] == record_id
    assert "result" in detail_data
    assert "top_words" in detail_data["result"]

    # 4. Query history stats
    stats_res = client.get("/api/v1/history/stats")
    assert stats_res.status_code == 200
    assert stats_res.json()["total_runs"] >= 1

    # 5. Delete history record
    del_res = client.delete(f"/api/v1/history/{record_id}")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # 6. Verify 404 after deletion
    not_found_res = client.get(f"/api/v1/history/{record_id}")
    assert not_found_res.status_code == 404
