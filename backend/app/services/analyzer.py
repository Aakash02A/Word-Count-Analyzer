import time
from collections import Counter
from typing import List, Optional

from app.schemas.analysis import (
    AnalysisMetadata,
    AnalysisResponse,
    BigramItem,
    SentimentResult,
    WordFrequencyItem,
    WordLengthItem,
)
from app.services.nlp_service import nlp_service
from app.services.preprocessor import TextPreprocessor
from app.services.spark_service import spark_service


class TextAnalyzer:
    """
    Core analytics service computing token statistics, frequency tables,
    word length distributions, bigram patterns, and NLP sentiment / noun phrases.
    Supports both Python standard execution and Apache PySpark DataFrame pipeline.
    """

    @classmethod
    def analyze(
        cls,
        text: str,
        top_n: int = 10,
        case_sensitive: bool = False,
        engine: str = "python",
        source_type: str = "text",
        source_name: Optional[str] = None,
    ) -> AnalysisResponse:
        """
        Runs text analytics and NLP insights on input text.
        Produces deterministic, reproducible outputs using either standard Python or PySpark.
        """
        start_time = time.perf_counter()

        raw_char_count = len(text)
        normalized_text = TextPreprocessor.normalize_text(text)
        norm_char_count = len(normalized_text)

        tokens = TextPreprocessor.tokenize(text, case_sensitive=case_sensitive)
        total_tokens = len(tokens)

        # NLP Sentiment & Noun Phrases
        sentiment = nlp_service.analyze_sentiment(text)
        noun_phrases = nlp_service.extract_noun_phrases(text, max_phrases=top_n)

        if total_tokens == 0:
            exec_time_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return AnalysisResponse(
                total_tokens=0,
                unique_tokens=0,
                average_word_length=0.0,
                top_words=[],
                word_frequencies=[],
                word_length_distribution=[],
                bigrams=[],
                sentiment=sentiment,
                noun_phrases=noun_phrases,
                metadata=AnalysisMetadata(
                    raw_character_count=raw_char_count,
                    normalized_character_count=norm_char_count,
                    case_sensitive=case_sensitive,
                    top_n_requested=top_n,
                    engine_used=engine,
                    source_type=source_type,
                    source_name=source_name,
                    execution_time_ms=exec_time_ms,
                    spark_version=None,
                ),
            )

        spark_ver: Optional[str] = None
        actual_engine = "python"

        # PySpark Processing Path
        if engine.lower() == "pyspark" and spark_service.is_pyspark_installed():
            try:
                session = spark_service.get_or_create_session()
                if session is not None:
                    spark_ver = session.version
                    (
                        word_frequencies,
                        word_length_distribution,
                        bigram_items,
                    ) = spark_service.analyze_tokens(tokens, top_n=top_n)

                    unique_tokens = len(word_frequencies)
                    top_words = word_frequencies[:top_n]

                    total_chars = sum(item.length * item.count for item in word_length_distribution)
                    avg_word_length = round(total_chars / total_tokens, 2) if total_tokens > 0 else 0.0

                    actual_engine = "pyspark"

                    exec_time_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
                    return AnalysisResponse(
                        total_tokens=total_tokens,
                        unique_tokens=unique_tokens,
                        average_word_length=avg_word_length,
                        top_words=top_words,
                        word_frequencies=word_frequencies,
                        word_length_distribution=word_length_distribution,
                        bigrams=bigram_items,
                        sentiment=sentiment,
                        noun_phrases=noun_phrases,
                        metadata=AnalysisMetadata(
                            raw_character_count=raw_char_count,
                            normalized_character_count=norm_char_count,
                            case_sensitive=case_sensitive,
                            top_n_requested=top_n,
                            engine_used=actual_engine,
                            source_type=source_type,
                            source_name=source_name,
                            execution_time_ms=exec_time_ms,
                            spark_version=spark_ver,
                        ),
                    )
            except Exception:
                actual_engine = "python"

        # Standard Python Processing Path (deterministic baseline)
        counts = Counter(tokens)
        unique_tokens = len(counts)

        sorted_word_counts = sorted(
            counts.items(),
            key=lambda item: (-item[1], item[0]),
        )

        word_frequencies = [
            WordFrequencyItem(
                word=word,
                count=count,
                percentage=round((count / total_tokens) * 100.0, 2),
            )
            for word, count in sorted_word_counts
        ]

        top_words = word_frequencies[:top_n]

        # Word length distribution & average length
        length_counter = Counter(len(token) for token in tokens)
        total_chars_in_tokens = sum(len(token) for token in tokens)
        avg_word_length = round(total_chars_in_tokens / total_tokens, 2)

        sorted_length_dist = sorted(length_counter.items(), key=lambda item: item[0])
        word_length_distribution = [
            WordLengthItem(length=length, count=count)
            for length, count in sorted_length_dist
        ]

        # Bigram analysis
        bigrams = [
            f"{tokens[i]} {tokens[i+1]}"
            for i in range(len(tokens) - 1)
        ]
        bigram_counts = Counter(bigrams)

        sorted_bigrams = sorted(
            bigram_counts.items(),
            key=lambda item: (-item[1], item[0]),
        )

        bigram_items = [
            BigramItem(bigram=bg, count=count)
            for bg, count in sorted_bigrams[:top_n]
        ]

        exec_time_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        return AnalysisResponse(
            total_tokens=total_tokens,
            unique_tokens=unique_tokens,
            average_word_length=avg_word_length,
            top_words=top_words,
            word_frequencies=word_frequencies,
            word_length_distribution=word_length_distribution,
            bigrams=bigram_items,
            sentiment=sentiment,
            noun_phrases=noun_phrases,
            metadata=AnalysisMetadata(
                raw_character_count=raw_char_count,
                normalized_character_count=norm_char_count,
                case_sensitive=case_sensitive,
                top_n_requested=top_n,
                engine_used=actual_engine,
                source_type=source_type,
                source_name=source_name,
                execution_time_ms=exec_time_ms,
                spark_version=spark_ver,
            ),
        )
