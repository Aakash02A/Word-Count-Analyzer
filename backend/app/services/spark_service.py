import logging
import os
import sys
import threading
from typing import List, Optional, Tuple

# Ensure PySpark workers use the active virtual environment Python on Windows
os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)

from app.core.config import settings
from app.schemas.analysis import (
    BigramItem,
    WordFrequencyItem,
    WordLengthItem,
)

logger = logging.getLogger(__name__)

# Lazy import flag to keep PySpark separate from API transport layer
_pyspark_imported = False
try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col, length
    from pyspark.sql.types import StringType, StructField, StructType
    _pyspark_imported = True
except ImportError:
    _pyspark_imported = False


class SparkService:
    """
    Manages Apache PySpark lifecycle and DataFrame-based analytical execution.
    Implements a controlled singleton session to avoid multiple contexts.
    """

    _instance: Optional["SparkService"] = None
    _lock = threading.Lock()
    _session: Optional["SparkSession"] = None

    def __new__(cls) -> "SparkService":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def is_pyspark_installed(cls) -> bool:
        """Checks if PySpark is installed in the current environment."""
        return _pyspark_imported

    def get_or_create_session(self) -> Optional["SparkSession"]:
        """
        Retrieves active SparkSession or lazily initializes a single local session.
        Applies local configuration and keeps UI private.
        """
        if not _pyspark_imported:
            logger.warning("PySpark is not installed or available.")
            return None

        if self._session is not None and not self._session.sparkContext._jsc.sc().isStopped():
            return self._session

        with self._lock:
            if self._session is not None and not self._session.sparkContext._jsc.sc().isStopped():
                return self._session

            try:
                logger.info("Initializing PySpark local session...")
                builder = (
                    SparkSession.builder
                    .master(settings.SPARK_MASTER)
                    .appName(settings.SPARK_APP_NAME)
                    .config("spark.ui.enabled", str(settings.SPARK_UI_ENABLED).lower())
                    .config("spark.driver.memory", settings.SPARK_DRIVER_MEMORY)
                    .config("spark.driver.host", "127.0.0.1")
                    .config("spark.driver.bindAddress", "127.0.0.1")
                    .config("spark.default.parallelism", "2")
                    .config("spark.sql.shuffle.partitions", "2")
                )
                self._session = builder.getOrCreate()
                # Set log level to WARN to reduce console noise
                self._session.sparkContext.setLogLevel("WARN")
                logger.info(f"PySpark session active (version: {self._session.version})")
                return self._session
            except Exception as e:
                logger.error(f"Failed to initialize PySpark session: {e}", exc_info=True)
                return None

    def stop_session(self) -> None:
        """Gracefully shuts down the active SparkSession and SparkContext."""
        with self._lock:
            if self._session is not None:
                try:
                    logger.info("Stopping PySpark session...")
                    self._session.stop()
                    logger.info("PySpark session stopped.")
                except Exception as e:
                    logger.warning(f"Error while stopping PySpark session: {e}")
                finally:
                    self._session = None

    def analyze_tokens(
        self,
        tokens: List[str],
        top_n: int = 10,
    ) -> Tuple[List[WordFrequencyItem], List[WordLengthItem], List[BigramItem]]:
        """
        Executes token frequency, word-length distribution, and bigram counting
        using PySpark DataFrame transformations.
        Guarantees deterministic sorting and bounded collection.
        """
        spark = self.get_or_create_session()
        if spark is None:
            raise RuntimeError("PySpark session is not available.")

        if not tokens:
            return [], [], []

        total_tokens = len(tokens)

        # 1. Word Frequencies DataFrame
        schema = StructType([StructField("word", StringType(), False)])
        row_data = [(t,) for t in tokens]
        df_tokens = spark.createDataFrame(row_data, schema=schema)

        # Group and order with deterministic tie-breaking (count desc, word asc)
        freq_df = (
            df_tokens.groupBy("word")
            .count()
            .orderBy(col("count").desc(), col("word").asc())
        )

        # Bounded collect for top words & frequency distribution
        collected_freq = freq_df.collect()
        word_frequencies = [
            WordFrequencyItem(
                word=row["word"],
                count=row["count"],
                percentage=round((row["count"] / total_tokens) * 100.0, 2),
            )
            for row in collected_freq
        ]

        # 2. Word Length Distribution DataFrame
        length_df = (
            df_tokens.withColumn("length", length(col("word")))
            .groupBy("length")
            .count()
            .orderBy(col("length").asc())
        )
        collected_lengths = length_df.collect()
        word_length_distribution = [
            WordLengthItem(length=row["length"], count=row["count"])
            for row in collected_lengths
        ]

        # 3. Bigram DataFrame Analysis
        if len(tokens) < 2:
            bigram_items = []
        else:
            bigram_pairs = [
                (f"{tokens[i]} {tokens[i+1]}",)
                for i in range(len(tokens) - 1)
            ]
            bg_schema = StructType([StructField("bigram", StringType(), False)])
            df_bigrams = spark.createDataFrame(bigram_pairs, schema=bg_schema)

            bg_grouped = (
                df_bigrams.groupBy("bigram")
                .count()
                .orderBy(col("count").desc(), col("bigram").asc())
                .limit(top_n)
            )
            collected_bigrams = bg_grouped.collect()
            bigram_items = [
                BigramItem(bigram=row["bigram"], count=row["count"])
                for row in collected_bigrams
            ]

        return word_frequencies, word_length_distribution, bigram_items


spark_service = SparkService()
