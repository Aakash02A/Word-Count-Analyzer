import re
import unicodedata
from typing import List, Tuple


class TextPreprocessor:
    """
    Standard preprocessing pipeline for Word Intelligence text analytics.
    Handles whitespace normalization, case normalization, and tokenization.
    """

    # Matches words supporting unicode letters, numbers, and internal apostrophes/hyphens (e.g. "state-of-the-art", "don't")
    WORD_TOKEN_PATTERN = re.compile(r"\b[\w]+(?:['’\-][\w]+)*\b", re.UNICODE)

    @classmethod
    def normalize_text(cls, text: str) -> str:
        """
        Normalizes unicode characters and collapses contiguous whitespace.
        """
        if not text:
            return ""
        # Unicode normalization (NFC)
        normalized = unicodedata.normalize("NFC", text)
        # Collapse multiple whitespace characters into single space
        return re.sub(r"\s+", " ", normalized).strip()

    @classmethod
    def tokenize(
        cls,
        text: str,
        case_sensitive: bool = False,
    ) -> List[str]:
        """
        Tokenizes text into individual words based on the defined tokenization policy.
        Removes leading/trailing punctuation and handles casing.
        """
        if not text:
            return []

        cleaned = cls.normalize_text(text)
        if not case_sensitive:
            cleaned = cleaned.lower()

        # Find all valid tokens
        tokens = cls.WORD_TOKEN_PATTERN.findall(cleaned)
        
        # Clean any remaining empty tokens
        return [t.strip() for t in tokens if t.strip()]
