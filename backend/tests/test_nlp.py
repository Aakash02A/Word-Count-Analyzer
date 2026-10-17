import pytest
from app.services.nlp_service import NLPService


def test_sentiment_positive():
    text = "Word Intelligence is an outstanding, wonderful, and extraordinary tool."
    sentiment = NLPService.analyze_sentiment(text)
    assert sentiment.label == "positive"
    assert sentiment.polarity > 0.1


def test_sentiment_negative():
    text = "The application crashed with a terrible, horrible, and dreadful defect."
    sentiment = NLPService.analyze_sentiment(text)
    assert sentiment.label == "negative"
    assert sentiment.polarity < -0.1


def test_sentiment_neutral():
    text = "The server returned HTTP status code 200 on port 8000."
    sentiment = NLPService.analyze_sentiment(text)
    assert sentiment.label == "neutral"


def test_sentiment_empty_input():
    sentiment = NLPService.analyze_sentiment("")
    assert sentiment.label == "neutral"
    assert sentiment.polarity == 0.0


def test_noun_phrases_extraction():
    text = "Artificial intelligence and big data analytics transform modern business operations."
    phrases = NLPService.extract_noun_phrases(text)
    assert isinstance(phrases, list)
    assert len(phrases) > 0
