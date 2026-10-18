from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class AnalysisRequest(BaseModel):
    """Request payload for raw text analysis."""
    text: str = Field(
        ...,
        min_length=1,
        description="The raw text content to analyze.",
        examples=["Java is powerful. Java is popular."],
    )
    top_n: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of top frequent words to return.",
    )
    case_sensitive: bool = Field(
        default=False,
        description="Whether word frequency counting should preserve case.",
    )
    engine: str = Field(
        default="python",
        description="Processing engine: 'python' (standard) or 'pyspark' (Apache Spark DataFrame pipeline).",
    )


class UrlAnalysisRequest(BaseModel):
    """Request payload for webpage URL analysis."""
    url: str = Field(
        ...,
        description="Public HTTP or HTTPS webpage URL to fetch and analyze.",
        examples=["https://example.com"],
    )
    top_n: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of top frequent words to return.",
    )
    case_sensitive: bool = Field(
        default=False,
        description="Whether word frequency counting should preserve case.",
    )
    engine: str = Field(
        default="python",
        description="Processing engine: 'python' or 'pyspark'.",
    )


class WordFrequencyItem(BaseModel):
    """Frequency metric for a single token."""
    word: str
    count: int
    percentage: float = Field(
        ...,
        description="Percentage of this token relative to total tokens.",
    )


class WordLengthItem(BaseModel):
    """Word length distribution bucket."""
    length: int
    count: int


class BigramItem(BaseModel):
    """Adjacent two-token sequence and occurrence count."""
    bigram: str
    count: int


class SentimentResult(BaseModel):
    """Sentiment analysis estimation and subjectivity score."""
    polarity: float = Field(..., description="Estimated polarity between -1.0 (negative) and 1.0 (positive).")
    subjectivity: float = Field(..., description="Estimated subjectivity between 0.0 (objective) and 1.0 (subjective).")
    label: str = Field(..., description="Categorical label: 'positive', 'neutral', or 'negative'.")


class AnalysisMetadata(BaseModel):
    """Metadata regarding preprocessing, extraction, and execution."""
    raw_character_count: int
    normalized_character_count: int
    case_sensitive: bool
    top_n_requested: int
    engine_used: str = "python"
    source_type: str = "text"
    source_name: Optional[str] = None
    execution_time_ms: Optional[float] = None
    spark_version: Optional[str] = None
    ocr_metadata: Optional[dict] = None


class AnalysisResponse(BaseModel):
    """Complete structured response for text analytics and NLP insights."""
    total_tokens: int
    unique_tokens: int
    average_word_length: float
    top_words: List[WordFrequencyItem]
    word_frequencies: List[WordFrequencyItem]
    word_length_distribution: List[WordLengthItem]
    bigrams: List[BigramItem]
    sentiment: Optional[SentimentResult] = None
    noun_phrases: List[str] = []
    extracted_text: Optional[str] = None
    metadata: AnalysisMetadata
