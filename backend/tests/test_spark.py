import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.analyzer import TextAnalyzer
from app.services.preprocessor import TextPreprocessor
from app.services.spark_service import SparkService, spark_service


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module", autouse=True)
def teardown_spark():
    """Ensures Spark is cleanly stopped after the test module finishes."""
    yield
    spark_service.stop_session()


def test_spark_service_singleton():
    """Verify SparkService maintains a singleton instance and reuses the session."""
    service1 = SparkService()
    service2 = spark_service
    assert service1 is service2

    session1 = service1.get_or_create_session()
    assert session1 is not None

    session2 = service2.get_or_create_session()
    assert session1 is session2


def test_spark_numerical_correctness_against_python():
    """
    Verify PySpark DataFrame transformations produce exact identical numerical results
    compared to the standard Python TextAnalyzer.
    """
    text = "Apache PySpark provides distributed DataFrame analytics. PySpark is fast and PySpark is reliable."
    tokens = TextPreprocessor.tokenize(text, case_sensitive=False)

    # 1. Standard Python results
    python_res = TextAnalyzer.analyze(text=text, top_n=10, case_sensitive=False, engine="python")

    # 2. PySpark DataFrame results
    spark_freq, spark_lengths, spark_bigrams = spark_service.analyze_tokens(tokens, top_n=10)

    # Numerical verifications
    assert len(spark_freq) == python_res.unique_tokens

    # Verify top word counts and words match exactly
    for py_item, sp_item in zip(python_res.word_frequencies, spark_freq):
        assert py_item.word == sp_item.word
        assert py_item.count == sp_item.count
        assert py_item.percentage == sp_item.percentage

    # Verify word length distributions match exactly
    py_lengths = {item.length: item.count for item in python_res.word_length_distribution}
    sp_lengths = {item.length: item.count for item in spark_lengths}
    assert py_lengths == sp_lengths

    # Verify bigrams match exactly
    py_bg = {item.bigram: item.count for item in python_res.bigrams}
    sp_bg = {item.bigram: item.count for item in spark_bigrams}
    assert py_bg == sp_bg


def test_api_analysis_with_pyspark_engine(client: TestClient):
    """Verify POST /api/v1/analysis executes successfully with engine='pyspark'."""
    payload = {
        "text": "PySpark big data analytics framework.",
        "top_n": 5,
        "engine": "pyspark",
    }
    response = client.post("/api/v1/analysis", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_tokens"] == 5
    assert data["metadata"]["engine_used"] == "pyspark"
    assert data["metadata"]["spark_version"] is not None
    assert data["metadata"]["execution_time_ms"] is not None
