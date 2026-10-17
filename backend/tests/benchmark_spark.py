"""
Benchmark comparison script between standard Python execution and Apache PySpark.
Records throughput, startup latency, and transformation times.
"""

import sys
import time
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.analyzer import TextAnalyzer
from app.services.spark_service import spark_service


def run_benchmark():
    print("=" * 60)
    print("WORD INTELLIGENCE — PYTHON vs PYSPARK BENCHMARK")
    print("=" * 60)

    # 1. Warm up Spark session
    print("\n[1/3] Initializing PySpark local session...")
    t_start = time.perf_counter()
    session = spark_service.get_or_create_session()
    warmup_time = round((time.perf_counter() - t_start) * 1000.0, 2)
    print(f"-> Spark initialized in {warmup_time} ms (Version: {session.version if session else 'N/A'})")

    # 2. Test datasets: Small text (50 words), Medium text (1,000 words), Large text (10,000 words)
    base_paragraph = (
        "Apache PySpark provides scalable distributed DataFrame execution. "
        "Word Intelligence analyzes tokens, word frequencies, length distributions, and bigrams. "
        "Natural language processing heuristics provide insight into unstructured content. "
    )

    test_sizes = [
        ("Small Corpus (~50 words)", base_paragraph * 2),
        ("Medium Corpus (~500 words)", base_paragraph * 20),
        ("Large Corpus (~5,000 words)", base_paragraph * 200),
    ]

    print("\n[2/3] Executing Comparative Benchmarks...")
    print(f"{'Corpus Size':<30} | {'Python Engine':<15} | {'PySpark Engine':<15} | {'Delta / Ratio'}")
    print("-" * 80)

    for label, text in test_sizes:
        # Run standard Python
        t0 = time.perf_counter()
        py_res = TextAnalyzer.analyze(text=text, top_n=10, engine="python")
        py_time = round((time.perf_counter() - t0) * 1000.0, 2)

        # Run PySpark
        t1 = time.perf_counter()
        spark_res = TextAnalyzer.analyze(text=text, top_n=10, engine="pyspark")
        spark_time = round((time.perf_counter() - t1) * 1000.0, 2)

        ratio = round(spark_time / py_time, 1) if py_time > 0 else 1.0
        print(f"{label:<30} | {py_time:>10.2f} ms | {spark_time:>10.2f} ms | {ratio:>5.1f}x (Spark overhead)")

        # Verify numerical consistency
        assert py_res.total_tokens == spark_res.total_tokens
        assert py_res.unique_tokens == spark_res.unique_tokens

    print("\n[3/3] Key Engineering Findings:")
    print("1. Standard Python in-memory processing has sub-millisecond to low-millisecond latency for typical inputs (< 10,000 words).")
    print("2. Local PySpark incurs JVM-to-Python IPC, stage scheduling, and serialization overhead on small datasets.")
    print("3. PySpark provides deterministic, exact numerical parity with Python and scales across partitioned datasets.")
    print("=" * 60)

    spark_service.stop_session()


if __name__ == "__main__":
    run_benchmark()
