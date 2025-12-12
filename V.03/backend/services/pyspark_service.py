"""
PySpark Analyzer Service - Distributed text analysis
"""
import time
from typing import Dict, Any
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, split, lower, regexp_replace, length, count, avg, countDistinct
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class PySparkService:
    """PySpark distributed analysis service"""
    
    def __init__(self):
        """Initialize Spark session"""
        self.spark = SparkSession.builder \
            .appName("WordIntelligence") \
            .master("local[*]") \
            .config("spark.driver.memory", "4g") \
            .config("spark.executor.memory", "2g") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("ERROR")
        self.jobs = {}
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text using PySpark"""
        start_time = time.time()
        
        try:
            # Create RDD from text
            lines_rdd = self.spark.sparkContext.parallelize(text.split('\n'))
            
            # Split into words
            words_rdd = lines_rdd \
                .flatMap(lambda line: line.split()) \
                .map(lambda word: word.lower().strip('.,!?;:')) \
                .filter(lambda word: len(word) > 2)
            
            # Create DataFrame
            words_df = words_rdd.toDF(["word"])
            
            # Calculate statistics
            word_counts = words_df.groupBy("word").count().orderBy(col("count").desc())
            total_words = word_counts.rdd.map(lambda row: row["count"]).sum()
            unique_words = word_counts.count()
            
            # Get top words
            top_words = word_counts.limit(50).collect()
            
            # Calculate word length distribution
            words_with_length = words_df.withColumn("length", length(col("word")))
            length_stats = words_with_length.groupBy("length").count().collect()
            
            # Sentiment (mock implementation)
            positive_words = {"good", "great", "excellent", "amazing", "wonderful", "beautiful"}
            negative_words = {"bad", "terrible", "awful", "horrible", "ugly", "disgusting"}
            
            # Convert to Python for processing
            all_words_list = [row["word"] for row in words_df.collect()]
            
            positive_count = sum(1 for w in all_words_list if w in positive_words)
            negative_count = sum(1 for w in all_words_list if w in negative_words)
            
            sentiment_score = (positive_count - negative_count) / max(len(all_words_list), 1) * 10
            sentiment_score = max(0, min(10, sentiment_score + 5))  # Normalize to 0-10
            
            execution_time = time.time() - start_time
            
            return {
                "total_words": int(total_words),
                "unique_words": int(unique_words),
                "average_word_length": sum(len(w) for w in all_words_list) / len(all_words_list) if all_words_list else 0,
                "top_words": [
                    {"word": row["word"], "count": int(row["count"])}
                    for row in top_words
                ],
                "sentiment_score": round(sentiment_score, 2),
                "length_distribution": [
                    {"length": row["length"], "count": int(row["count"])}
                    for row in length_stats
                ],
                "execution_time": round(execution_time, 2)
            }
        
        except Exception as e:
            logger.error(f"PySpark analysis error: {str(e)}")
            return {
                "error": str(e),
                "total_words": 0,
                "unique_words": 0,
                "execution_time": time.time() - start_time
            }
    
    def submit_job(self, analysis_id: str, text: str) -> str:
        """Submit analysis job"""
        job_id = f"job_{analysis_id}_{int(time.time())}"
        self.jobs[job_id] = {
            "status": "running",
            "analysis_id": analysis_id,
            "progress": 0
        }
        
        # Run analysis
        result = self.analyze_text(text)
        self.jobs[job_id]["status"] = "completed"
        self.jobs[job_id]["result"] = result
        self.jobs[job_id]["progress"] = 100
        
        return job_id
    
    def get_job_status(self, job_id: str) -> str:
        """Get job status"""
        if job_id in self.jobs:
            return self.jobs[job_id]["status"]
        return "unknown"
    
    def get_job_metrics(self, job_id: str) -> Dict[str, Any]:
        """Get job metrics"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            return {
                "status": job["status"],
                "progress": job["progress"],
                "result": job.get("result", {})
            }
        return {"status": "unknown"}
    
    def get_logs(self, job_id: str) -> str:
        """Get job logs"""
        return f"Logs for job {job_id}"
    
    def stop(self):
        """Stop Spark session"""
        if self.spark:
            self.spark.stop()
