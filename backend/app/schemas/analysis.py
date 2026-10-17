from typing import Dict, List, Optional
from pydantic import BaseModel, Field


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
    include_punctuation: bool = Field(
        default=False,
        description="Whether punctuation characters should be kept inside tokens.",
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


class AnalysisMetadata(BaseModel):
    """Metadata regarding preprocessing and execution."""
    raw_character_count: int
    normalized_character_count: int
    case_sensitive: bool
    top_n_requested: int


class AnalysisResponse(BaseModel):
    """Complete structured response for text analytics."""
    total_tokens: int
    unique_tokens: int
    average_word_length: float
    top_words: List[WordFrequencyItem]
    word_frequencies: List[WordFrequencyItem]
    word_length_distribution: List[WordLengthItem]
    bigrams: List[BigramItem]
    metadata: AnalysisMetadata
