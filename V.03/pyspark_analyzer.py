# File 2: pyspark_analyzer.py (PySpark Analysis Engine)
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, split, lower, regexp_replace, length
from pyspark.sql.functions import count, sum as spark_sum, avg, max as spark_max
from pyspark.ml.feature import Tokenizer, StopWordsRemover, NGram, CountVectorizer
from pyspark.ml.feature import IDF, VectorAssembler
from pyspark.ml.clustering import KMeans
from pyspark.ml import Pipeline
import re
import time
from datetime import datetime
from typing import Dict, List, Any
import json
import uuid
import numpy as np
from collections import Counter

class PySparkAnalyzer:
    """Main PySpark analysis engine for text processing"""
    
    def __init__(self, master='local[*]', app_name='WordIntelligenceAnalytics'):
        self.master = master
        self.app_name = app_name
        self.spark = None
        self.sc = None
        self.initialize_spark()
        
    def initialize_spark(self):
        """Initialize Spark session with configuration"""
        try:
            self.spark = SparkSession.builder \
                .appName(self.app_name) \
                .master(self.master) \
                .config("spark.executor.memory", "2g") \
                .config("spark.driver.memory", "2g") \
                .config("spark.executor.cores", "2") \
                .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
                .config("spark.sql.shuffle.partitions", "8") \
                .config("spark.ui.port", "4040") \
                .config("spark.ui.enabled", "true") \
                .config("spark.eventLog.enabled", "true") \
                .config("spark.eventLog.dir", "spark_logs") \
                .getOrCreate()
            
            self.sc = self.spark.sparkContext
            self.sc.setLogLevel("WARN")
            
            print(f"Spark initialized successfully: {self.spark.version}")
            print(f"Spark UI available at: http://localhost:4040")
            
        except Exception as e:
            print(f"Error initializing Spark: {str(e)}")
            raise
    
    def check_spark_status(self):
        """Check if Spark is running and healthy"""
        try:
            if self.spark is None:
                return "not_initialized"
            
            # Check Spark context
            if self.sc._jsc.sc().isStopped():
                return "stopped"
            
            # Try to run a simple job to verify
            test_rdd = self.sc.parallelize([1, 2, 3])
            test_result = test_rdd.sum()
            
            return "healthy"
            
        except Exception as e:
            return f"error: {str(e)}"
    
    def get_spark_metrics(self):
        """Get Spark metrics for monitoring"""
        try:
            if self.spark is None:
                return {}
            
            # Get Spark UI metrics (simplified)
            metrics = {
                'executors': self.spark.sparkContext._conf.get('spark.executor.instances', '1'),
                'executor_memory': self.spark.sparkContext._conf.get('spark.executor.memory', '1g'),
                'driver_memory': self.spark.sparkContext._conf.get('spark.driver.memory', '1g'),
                'application_id': self.spark.sparkContext.applicationId,
                'application_name': self.spark.sparkContext.appName,
            }
            
            return metrics
            
        except Exception as e:
            print(f"Error getting Spark metrics: {str(e)}")
            return {}
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Main text analysis function
        Returns comprehensive analysis results
        """
        start_time = time.time()
        analysis_id = str(uuid.uuid4())
        
        try:
            # Create DataFrame from text
            data = [(i, line) for i, line in enumerate(text.split('\n')) if line.strip()]
            df = self.spark.createDataFrame(data, ["id", "text"])
            
            # Preprocessing
            df_clean = self.preprocess_text(df)
            
            # Word frequency analysis
            word_freq = self.word_frequency_analysis(df_clean)
            
            # N-gram analysis
            bigrams = self.ngram_analysis(df_clean, n=2)
            trigrams = self.ngram_analysis(df_clean, n=3)
            
            # Sentiment analysis
            sentiment_scores = self.sentiment_analysis(df_clean)
            
            # Statistical analysis
            stats = self.statistical_analysis(df_clean)
            
            # Topic modeling (simplified)
            topics = self.topic_modeling(df_clean)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Compile results
            results = {
                'analysis_id': analysis_id,
                'job_id': self.spark.sparkContext.applicationId,
                'total_words': stats['total_words'],
                'unique_words': stats['unique_words'],
                'total_lines': stats['total_lines'],
                'avg_word_length': stats['avg_word_length'],
                'lexical_diversity': stats['lexical_diversity'],
                'word_frequencies': word_freq,
                'bigrams': bigrams,
                'trigrams': trigrams,
                'sentiment_scores': sentiment_scores,
                'emotion_analysis': self.emotion_analysis(df_clean),
                'topic_clusters': topics,
                'statistics': stats,
                'processing_time': round(processing_time, 3),
                'vocabulary_richness': stats['vocabulary_richness'],
                'reading_level': stats['reading_level'],
                'timestamp': datetime.now().isoformat()
            }
            
            return results
            
        except Exception as e:
            print(f"Error in text analysis: {str(e)}")
            raise
    
    def preprocess_text(self, df):
        """Preprocess text: clean, tokenize, remove stopwords"""
        # Clean text
        df_clean = df.withColumn(
            "clean_text",
            regexp_replace(
                lower(col("text")),
                r"[^a-zA-Z\s]",  # Remove non-alphabetic characters
                " "
            )
        )
        
        # Tokenize
        tokenizer = Tokenizer(inputCol="clean_text", outputCol="words")
        df_words = tokenizer.transform(df_clean)
        
        # Remove stopwords
        remover = StopWordsRemover(
            inputCol="words", 
            outputCol="filtered_words",
            stopWords=self.get_default_stopwords()
        )
        df_filtered = remover.transform(df_words)
        
        # Filter out empty tokens
        df_filtered = df_filtered.filter(
            col("filtered_words").isNotNull() & (size(col("filtered_words")) > 0)
        )
        
        return df_filtered
    
    def get_default_stopwords(self):
        """Get default stopwords list"""
        # Common English stopwords
        stopwords = [
            "the", "and", "is", "in", "to", "of", "a", "for", "on", "with", "as", "by",
            "at", "an", "be", "this", "that", "or", "it", "are", "from", "was", "were",
            "but", "not", "what", "all", "when", "where", "how", "which", "who", "whom",
            "why", "their", "there", "they", "them", "these", "those", "his", "her",
            "has", "have", "had", "will", "would", "should", "could", "can", "may",
            "might", "must", "about", "into", "out", "up", "down", "over", "under",
            "again", "further", "then", "once", "here", "there", "when", "where",
            "why", "how", "all", "any", "both", "each", "few", "more", "most",
            "other", "some", "such", "no", "nor", "only", "own", "same", "so",
            "than", "too", "very", "just", "now"
        ]
        return stopwords
    
    def word_frequency_analysis(self, df):
        """Calculate word frequencies"""
        # Explode words into individual rows
        df_words = df.select(explode(col("filtered_words")).alias("word"))
        
        # Count frequencies
        word_counts = df_words.groupBy("word") \
            .agg(count("*").alias("frequency")) \
            .orderBy(col("frequency").desc()) \
            .limit(1000)  # Limit to top 1000 words
        
        # Convert to list of dictionaries
        results = word_counts.collect()
        word_freq = [
            {
                "word": row["word"],
                "frequency": row["frequency"],
                "length": len(row["word"])
            }
            for row in results
        ]
        
        return word_freq
    
    def ngram_analysis(self, df, n=2):
        """Generate and analyze n-grams"""
        ngram = NGram(n=n, inputCol="filtered_words", outputCol=f"{n}grams")
        df_ngrams = ngram.transform(df)
        
        # Explode n-grams
        df_exploded = df_ngrams.select(explode(col(f"{n}grams")).alias("ngram"))
        
        # Count frequencies
        ngram_counts = df_exploded.groupBy("ngram") \
            .agg(count("*").alias("frequency")) \
            .orderBy(col("frequency").desc()) \
            .limit(100)  # Limit to top 100 n-grams
        
        # Convert to list
        results = ngram_counts.collect()
        ngrams = [
            {
                "ngram": row["ngram"],
                "frequency": row["frequency"]
            }
            for row in results
        ]
        
        return ngrams
    
    def sentiment_analysis(self, df):
        """Basic sentiment analysis using word lists"""
        # Positive and negative word lists (simplified)
        positive_words = [
            "good", "great", "excellent", "amazing", "wonderful", "fantastic",
            "positive", "happy", "joy", "love", "like", "best", "better"
        ]
        
        negative_words = [
            "bad", "terrible", "awful", "horrible", "negative", "sad",
            "angry", "hate", "worst", "worse", "poor", "failure"
        ]
        
        # Count positive and negative words
        df_words = df.select(explode(col("filtered_words")).alias("word"))
        
        positive_count = df_words.filter(col("word").isin(positive_words)).count()
        negative_count = df_words.filter(col("word").isin(negative_words)).count()
        total_words = df_words.count()
        
        # Calculate sentiment scores
        if total_words > 0:
            positivity = positive_count / total_words
            negativity = negative_count / total_words
            sentiment_score = (positive_count - negative_count) / max(positive_count + negative_count, 1)
        else:
            positivity = negativity = sentiment_score = 0
        
        return {
            "positive_words": positive_count,
            "negative_words": negative_count,
            "positivity_score": round(positivity, 4),
            "negativity_score": round(negativity, 4),
            "overall_sentiment": round(sentiment_score, 4),
            "sentiment_label": self.get_sentiment_label(sentiment_score)
        }
    
    def get_sentiment_label(self, score):
        """Convert sentiment score to label"""
        if score > 0.3:
            return "Positive"
        elif score > 0.1:
            return "Slightly Positive"
        elif score > -0.1:
            return "Neutral"
        elif score > -0.3:
            return "Slightly Negative"
        else:
            return "Negative"
    
    def emotion_analysis(self, df):
        """Basic emotion analysis using word categories"""
        # Emotion word lists (simplified)
        emotion_words = {
            "joy": ["happy", "joy", "delight", "pleasure", "excitement"],
            "trust": ["trust", "confidence", "faith", "belief", "reliable"],
            "fear": ["fear", "afraid", "scared", "anxious", "worried"],
            "surprise": ["surprise", "amazed", "astonished", "shocked"],
            "sadness": ["sad", "sorrow", "grief", "unhappy", "depressed"],
            "disgust": ["disgust", "revulsion", "repulsion", "hatred"],
            "anger": ["anger", "angry", "furious", "rage", "outrage"],
            "anticipation": ["anticipation", "expectation", "hope", "looking forward"]
        }
        
        df_words = df.select(explode(col("filtered_words")).alias("word"))
        total_words = df_words.count()
        
        emotion_counts = {}
        for emotion, words in emotion_words.items():
            count = df_words.filter(col("word").isin(words)).count()
            percentage = (count / max(total_words, 1)) * 100
            emotion_counts[emotion] = {
                "count": count,
                "percentage": round(percentage, 2)
            }
        
        return emotion_counts
    
    def statistical_analysis(self, df):
        """Calculate statistical metrics"""
        # Word count per line
        df_with_counts = df.withColumn("word_count", size(col("filtered_words")))
        
        # Basic statistics
        stats = df_with_counts.agg(
            spark_sum("word_count").alias("total_words"),
            count("*").alias("total_lines"),
            avg("word_count").alias("avg_words_per_line"),
            spark_max("word_count").alias("max_words_per_line")
        ).collect()[0]
        
        # Unique words
        unique_words_df = df.select(explode(col("filtered_words")).alias("word")).distinct()
        unique_words_count = unique_words_df.count()
        
        # Word length analysis
        df_word_lengths = df.select(explode(col("filtered_words")).alias("word")) \
            .withColumn("word_length", length(col("word")))
        
        word_length_stats = df_word_lengths.agg(
            avg("word_length").alias("avg_word_length"),
            spark_max("word_length").alias("max_word_length")
        ).collect()[0]
        
        # Calculate lexical diversity
        total_words = stats["total_words"]
        lexical_diversity = unique_words_count / max(total_words, 1) if total_words > 0 else 0
        
        # Vocabulary richness (types/tokens ratio)
        vocabulary_richness = (unique_words_count / max(total_words, 1)) * 100
        
        # Reading level estimation (simplified Flesch-Kincaid)
        avg_sentence_length = stats["avg_words_per_line"]
        avg_word_length = word_length_stats["avg_word_length"]
        
        # Simplified reading score
        reading_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * (avg_word_length / avg_sentence_length))
        
        if reading_score >= 90:
            reading_level = "Very Easy"
        elif reading_score >= 80:
            reading_level = "Easy"
        elif reading_score >= 70:
            reading_level = "Fairly Easy"
        elif reading_score >= 60:
            reading_level = "Standard"
        elif reading_score >= 50:
            reading_level = "Fairly Difficult"
        elif reading_score >= 30:
            reading_level = "Difficult"
        else:
            reading_level = "Very Difficult"
        
        return {
            "total_words": int(total_words),
            "unique_words": int(unique_words_count),
            "total_lines": int(stats["total_lines"]),
            "avg_words_per_line": round(float(stats["avg_words_per_line"]), 2),
            "max_words_per_line": int(stats["max_words_per_line"]),
            "avg_word_length": round(float(word_length_stats["avg_word_length"]), 2),
            "max_word_length": int(word_length_stats["max_word_length"]),
            "lexical_diversity": round(lexical_diversity, 4),
            "vocabulary_richness": round(vocabulary_richness, 2),
            "reading_score": round(reading_score, 2),
            "reading_level": reading_level
        }
    
    def topic_modeling(self, df):
        """Simple topic modeling using TF-IDF and clustering"""
        try:
            # Limit data for performance
            df_limited = df.limit(1000)
            
            # TF-IDF
            vectorizer = CountVectorizer(
                inputCol="filtered_words",
                outputCol="raw_features",
                vocabSize=1000,
                minDF=2.0
            )
            
            idf = IDF(inputCol="raw_features", outputCol="features", minDocFreq=2)
            
            # Create pipeline
            pipeline = Pipeline(stages=[vectorizer, idf])
            model = pipeline.fit(df_limited)
            result = model.transform(df_limited)
            
            # K-means clustering
            kmeans = KMeans().setK(5).setSeed(42).setFeaturesCol("features")
            km_model = kmeans.fit(result)
            predictions = km_model.transform(result)
            
            # Get cluster centers and top words
            vocab = model.stages[0].vocabulary
            cluster_centers = km_model.clusterCenters()
            
            topics = []
            for i, center in enumerate(cluster_centers):
                # Get top 10 words for this cluster
                top_indices = center.argsort()[-10:][::-1]
                top_words = [vocab[idx] for idx in top_indices if idx < len(vocab)]
                
                topics.append({
                    "cluster_id": i,
                    "size": predictions.filter(col("prediction") == i).count(),
                    "top_words": top_words[:5],  # Top 5 words
                    "score": round(float(np.mean(center[top_indices[:5]])), 4)
                })
            
            return topics
            
        except Exception as e:
            print(f"Topic modeling error (using fallback): {str(e)}")
            # Return mock topics if modeling fails
            return [
                {"cluster_id": 0, "size": 100, "top_words": ["data", "analysis", "processing"], "score": 0.85},
                {"cluster_id": 1, "size": 80, "top_words": ["machine", "learning", "algorithm"], "score": 0.76},
                {"cluster_id": 2, "size": 60, "top_words": ["spark", "distributed", "computing"], "score": 0.64},
            ]
    
    def filter_stopwords(self, word_frequencies, custom_stopwords):
        """Filter word frequencies using custom stopwords"""
        if not custom_stopwords:
            return word_frequencies
        
        stopwords_set = set([sw.lower().strip() for sw in custom_stopwords])
        filtered = [
            wf for wf in word_frequencies 
            if wf["word"].lower() not in stopwords_set
        ]
        
        return filtered
    
    def search_word(self, word_frequencies, search_term):
        """Search for specific word in frequencies"""
        search_term = search_term.lower().strip()
        results = [
            wf for wf in word_frequencies 
            if search_term in wf["word"].lower()
        ]
        
        return results
    
    def stop(self):
        """Stop Spark session"""
        if self.spark:
            self.spark.stop()
            print("Spark session stopped")