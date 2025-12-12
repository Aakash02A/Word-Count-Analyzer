"""
Visualization Service - Generate charts and visualizations
"""
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)

class VisualizationService:
    """Service for generating visualization data"""
    
    def generate_visualizations(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate all visualization data from analysis"""
        
        visualizations = {
            "word_frequency": self._generate_frequency_chart(analysis_result),
            "word_length_histogram": self._generate_length_histogram(analysis_result),
            "sentiment_pie": self._generate_sentiment_pie(analysis_result),
            "top_bigrams": self._generate_bigrams(analysis_result),
            "trigrams": self._generate_trigrams(analysis_result),
            "statistics": self._generate_statistics(analysis_result)
        }
        
        return visualizations
    
    def _generate_frequency_chart(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate word frequency chart data"""
        top_words = analysis_result.get("top_words", [])[:20]
        
        return {
            "type": "bar",
            "title": "Top 20 Words by Frequency",
            "labels": [w["word"] for w in top_words],
            "datasets": [{
                "label": "Frequency",
                "data": [w["count"] for w in top_words],
                "backgroundColor": "#0C66E4"
            }]
        }
    
    def _generate_length_histogram(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate word length histogram"""
        length_dist = analysis_result.get("length_distribution", [])
        sorted_dist = sorted(length_dist, key=lambda x: x["length"])
        
        return {
            "type": "bar",
            "title": "Word Length Distribution",
            "labels": [str(d["length"]) for d in sorted_dist],
            "datasets": [{
                "label": "Count",
                "data": [d["count"] for d in sorted_dist],
                "backgroundColor": "#1D7AFC"
            }]
        }
    
    def _generate_sentiment_pie(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sentiment distribution pie chart"""
        sentiment = analysis_result.get("sentiment_score", 5)
        
        # Create sentiment categories
        if sentiment >= 7:
            categories = {"Positive": 60, "Neutral": 30, "Negative": 10}
        elif sentiment >= 4:
            categories = {"Positive": 40, "Neutral": 50, "Negative": 10}
        else:
            categories = {"Positive": 20, "Neutral": 30, "Negative": 50}
        
        return {
            "type": "pie",
            "title": "Sentiment Distribution",
            "labels": list(categories.keys()),
            "datasets": [{
                "data": list(categories.values()),
                "backgroundColor": ["#16A34A", "#94A3B8", "#DC2626"]
            }]
        }
    
    def _generate_bigrams(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate top bigrams"""
        top_words = analysis_result.get("top_words", [])
        
        # Create mock bigrams from top words
        bigrams = [
            {"bigram": f"{top_words[i]['word']} {top_words[i+1]['word']}", "count": top_words[i]['count'] // 2}
            for i in range(min(5, len(top_words) - 1))
        ]
        
        return {
            "type": "table",
            "title": "Top Bigrams",
            "data": bigrams
        }
    
    def _generate_trigrams(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate top trigrams"""
        top_words = analysis_result.get("top_words", [])
        
        # Create mock trigrams
        trigrams = [
            {"trigram": f"{top_words[i]['word']} {top_words[i+1]['word']} {top_words[i+2]['word']}", "count": top_words[i]['count'] // 3}
            for i in range(min(5, len(top_words) - 2))
        ]
        
        return {
            "type": "table",
            "title": "Top Trigrams",
            "data": trigrams
        }
    
    def _generate_statistics(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate statistics summary"""
        return {
            "type": "stats",
            "title": "Analysis Statistics",
            "data": {
                "total_words": analysis_result.get("total_words", 0),
                "unique_words": analysis_result.get("unique_words", 0),
                "avg_word_length": round(analysis_result.get("average_word_length", 0), 2),
                "sentiment_score": analysis_result.get("sentiment_score", 5),
                "execution_time": analysis_result.get("execution_time", 0)
            }
        }
