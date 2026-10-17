import logging
from typing import List, Tuple

from app.schemas.analysis import SentimentResult

logger = logging.getLogger(__name__)

# Try importing TextBlob safely
_textblob_available = False
try:
    from textblob import TextBlob
    _textblob_available = True
except ImportError:
    logger.warning("TextBlob is not installed or available.")


class NLPService:
    """
    Natural Language Processing service providing sentiment polarity estimation
    and noun phrase discovery with resilient error handling.
    """

    POSITIVE_THRESHOLD = 0.1
    NEGATIVE_THRESHOLD = -0.1

    @classmethod
    def analyze_sentiment(cls, text: str) -> SentimentResult:
        """
        Estimates sentiment polarity and subjectivity using TextBlob heuristics.
        Returns a classified SentimentResult ('positive', 'neutral', 'negative').
        """
        if not text or not text.strip() or not _textblob_available:
            return SentimentResult(polarity=0.0, subjectivity=0.0, label="neutral")

        try:
            blob = TextBlob(text)
            polarity = round(float(blob.sentiment.polarity), 2)
            subjectivity = round(float(blob.sentiment.subjectivity), 2)

            if polarity > cls.POSITIVE_THRESHOLD:
                label = "positive"
            elif polarity < cls.NEGATIVE_THRESHOLD:
                label = "negative"
            else:
                label = "neutral"

            return SentimentResult(
                polarity=polarity,
                subjectivity=subjectivity,
                label=label,
            )
        except Exception as e:
            logger.warning(f"Sentiment analysis encountered an error: {e}")
            return SentimentResult(polarity=0.0, subjectivity=0.0, label="neutral")

    @classmethod
    def extract_noun_phrases(cls, text: str, max_phrases: int = 20) -> List[str]:
        """
        Discovers key noun phrases from text.
        Returns a deduplicated, case-normalized list of up to max_phrases.
        """
        if not text or not text.strip() or not _textblob_available:
            return []

        try:
            blob = TextBlob(text)
            # Deduplicate preserving order
            seen = set()
            phrases = []
            for phrase in blob.noun_phrases:
                cleaned = str(phrase).lower().strip()
                if cleaned and cleaned not in seen and len(cleaned) > 2:
                    seen.add(cleaned)
                    phrases.append(cleaned)
                    if len(phrases) >= max_phrases:
                        break
            return phrases
        except Exception as e:
            logger.warning(f"Noun phrase extraction encountered an error: {e}")
            return []


nlp_service = NLPService()
