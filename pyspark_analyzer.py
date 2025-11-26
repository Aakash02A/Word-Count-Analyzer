"""
PySpark-based text analyzer for the Word Count Analyzer application.
This module provides PySpark implementations for text processing.
"""

import re
from collections import Counter

# Initialize global variables for PySpark components
SparkSession = None
split = None
explode = None
lower = None
col = None
PYSPARK_AVAILABLE = False

try:
    from pyspark.sql import SparkSession as SparkSessionImport
    from pyspark.sql.functions import split as splitImport, explode as explodeImport, lower as lowerImport, col as colImport
    SparkSession = SparkSessionImport
    split = splitImport
    explode = explodeImport
    lower = lowerImport
    col = colImport
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False
    print("PySpark not available. Install PySpark for enhanced text analysis capabilities.")


def analyze_text_with_pyspark(file_path, stopwords=None):
    """
    Analyze text file using PySpark to count word frequencies.
    
    Args:
        file_path (str): Path to the text file to analyze
        stopwords (set, optional): Set of words to exclude from analysis
        
    Returns:
        tuple: (all_words_list, filtered_words_list) - Lists of all words and filtered words
    """
    if not PYSPARK_AVAILABLE:
        raise ImportError("PySpark is not available. Please install PySpark to use this feature.")
    
    try:
        # Create Spark session if not exists
        spark = SparkSession.builder.appName("WordCountAnalyzer").getOrCreate()
        
        # Read text file
        text_df = spark.read.text(file_path)
        
        # Preprocess text: convert to lowercase and split into words
        words_df = text_df.select(
            explode(
                split(
                    lower(col("value")), 
                    "[^a-zA-Z]+"
                )
            ).alias("word")
        ).filter(col("word") != "")
        
        # Filter out stopwords if provided
        if stopwords:
            # Convert stopwords to lowercase for case-insensitive comparison
            stopwords_lower = [word.lower() for word in stopwords]
            filtered_words_df = words_df.filter(~col("word").isin(stopwords_lower))
        else:
            filtered_words_df = words_df
            
        # Count word frequencies
        word_counts_df = filtered_words_df.groupBy("word").count().orderBy(col("count").desc())
        
        # Collect results
        word_counts = word_counts_df.collect()
        
        # Extract words and counts
        words = [row["word"] for row in word_counts]
        counts = [row["count"] for row in word_counts]
        
        # For all words (without stopwords filtering), we need to do another count
        all_word_counts_df = words_df.groupBy("word").count().orderBy(col("count").desc())
        all_word_counts = all_word_counts_df.collect()
        all_words = [row["word"] for row in all_word_counts]
        all_counts = [row["count"] for row in all_word_counts]
        
        # Stop Spark session to free resources
        spark.stop()
        
        return (all_words, words)
    except Exception as e:
        # If PySpark fails, fall back to basic Python implementation
        print(f"PySpark analysis failed, falling back to Python implementation: {e}")
        return _fallback_python_implementation(file_path, stopwords)


def _fallback_python_implementation(file_path, stopwords=None):
    """Fallback implementation using basic Python."""
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        
        # Clean and tokenize text
        text = re.sub(r'[^A-Za-z\s]', '', text).lower()
        all_words = [w for w in text.split() if w]
        
        # Apply stopwords filtering if provided
        if stopwords:
            stopwords_lower = {word.lower() for word in stopwords}
            filtered_words = [w for w in all_words if w not in stopwords_lower]
        else:
            filtered_words = all_words
            
        return (all_words, filtered_words)
    except Exception as e:
        print(f"Fallback implementation also failed: {e}")
        return ([], [])


def is_pyspark_available():
    """Check if PySpark is available for use."""
    return PYSPARK_AVAILABLE


if __name__ == "__main__":
    # Example usage
    if is_pyspark_available():
        print("PySpark is available")
    else:
        print("PySpark is not available")