from collections import Counter
from typing import List

from app.schemas.analysis import (
    AnalysisMetadata,
    AnalysisResponse,
    BigramItem,
    WordFrequencyItem,
    WordLengthItem,
)
from app.services.preprocessor import TextPreprocessor


class TextAnalyzer:
    """
    Core analytics service computing token statistics, frequency tables,
    word length distributions, and bigram patterns.
    """

    @classmethod
    def analyze(
        cls,
        text: str,
        top_n: int = 10,
        case_sensitive: bool = False,
    ) -> AnalysisResponse:
        """
        Runs complete text analytics on input text.
        Produces deterministic, reproducible outputs.
        """
        raw_char_count = len(text)
        normalized_text = TextPreprocessor.normalize_text(text)
        norm_char_count = len(normalized_text)

        tokens = TextPreprocessor.tokenize(text, case_sensitive=case_sensitive)
        total_tokens = len(tokens)

        if total_tokens == 0:
            return AnalysisResponse(
                total_tokens=0,
                unique_tokens=0,
                average_word_length=0.0,
                top_words=[],
                word_frequencies=[],
                word_length_distribution=[],
                bigrams=[],
                metadata=AnalysisMetadata(
                    raw_character_count=raw_char_count,
                    normalized_character_count=norm_char_count,
                    case_sensitive=case_sensitive,
                    top_n_requested=top_n,
                ),
            )

        # Word frequency counting
        counts = Counter(tokens)
        unique_tokens = len(counts)

        # Deterministic sorting: count descending, then alphabetical word ascending
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

        # Deterministic sorting: count descending, then alphabetical ascending
        sorted_bigrams = sorted(
            bigram_counts.items(),
            key=lambda item: (-item[1], item[0]),
        )

        bigram_items = [
            BigramItem(bigram=bg, count=count)
            for bg, count in sorted_bigrams[:top_n]
        ]

        return AnalysisResponse(
            total_tokens=total_tokens,
            unique_tokens=unique_tokens,
            average_word_length=avg_word_length,
            top_words=top_words,
            word_frequencies=word_frequencies,
            word_length_distribution=word_length_distribution,
            bigrams=bigram_items,
            metadata=AnalysisMetadata(
                raw_character_count=raw_char_count,
                normalized_character_count=norm_char_count,
                case_sensitive=case_sensitive,
                top_n_requested=top_n,
            ),
        )
