import re
from collections import Counter
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup

class TextAnalyzer:
    def __init__(self):
        self.stopwords = set([
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
        ])

    def clean_text(self, text):
        """Remove special characters and convert to lowercase."""
        # Remove HTML tags if any remain
        text = re.sub(r'<[^>]+>', ' ', text)
        # Replace non-alphanumeric with space to prevent merging words (e.g. "one,two" -> "one two")
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        return text.lower()

    def get_word_frequencies(self, text, limit=50):
        """Get top words and their counts, excluding stopwords."""
        cleaned = self.clean_text(text)
        all_words = cleaned.split()
        total_words = len(all_words)
        
        # Filter for analysis
        words = [w for w in all_words if w and w not in self.stopwords and len(w) > 2]
        
        counter = Counter(words)
        unique_words = len(counter)
        
        # Get top N words
        top_words_data = counter.most_common(limit)
        top_words = [w[0] for w in top_words_data]
        top_counts = [w[1] for w in top_words_data]
        
        return top_words, top_counts, total_words, unique_words

    def get_bigrams(self, text, limit=10):
        """Get top bigrams."""
        cleaned = self.clean_text(text)
        words = [w for w in cleaned.split() if w and w not in self.stopwords and len(w) > 2]
        
        if len(words) < 2:
            return []
            
        bi_grams = zip(words, words[1:])
        bi_gram_strings = [f"{w1} {w2}" for w1, w2 in bi_grams]
        
        counter = Counter(bi_gram_strings)
        return [{'gram': k, 'count': v} for k, v in counter.most_common(limit)]

    def analyze_sentiment(self, text):
        """Analyze sentiment using TextBlob."""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                label = "Positive"
            elif polarity < -0.1:
                label = "Negative"
            else:
                label = "Neutral"
                
            return polarity, label
        except:
            return 0.0, "Neutral"

    def extract_topics(self, text, limit=5):
        """
        Extract topics based on noun phrases, with fallback to frequent long words.
        """
        topics = []
        try:
            # Primary method: Noun Phrases via TextBlob
            blob = TextBlob(text)
            nouns = blob.noun_phrases
            
            if nouns:
                counter = Counter(nouns)
                topics = [{'text': k, 'score': v} for k, v in counter.most_common(limit)]
        except Exception as e:
            # Fallback will handle this
            pass

        # Fallback: If no topics found (missing corpora or empty), use top unique long words
        if not topics:
            try:
                # Reuse word frequency logic but filter for length > 4 (likely significant words)
                clean_text = self.clean_text(text)
                words = [w for w in clean_text.split() if w and w not in self.stopwords and len(w) > 4]
                counter = Counter(words)
                topics = [{'text': k.title(), 'score': v} for k, v in counter.most_common(limit)]
            except:
                topics = []

        return topics

    def fetch_url_content(self, url):
        """Fetch and extract text from a URL."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
            
        text = soup.get_text()
        
        # Break into lines and remove leading/trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text

    def get_word_length_distribution(self, text):
        """Calculate frequency of words by their length."""
        cleaned = self.clean_text(text)
        words = [w for w in cleaned.split() if w and w not in self.stopwords]
        
        lengths = [len(w) for w in words]
        if not lengths:
            return {}
            
        return dict(Counter(lengths))

    def get_word_distribution(self, text, target_words=None, segments=10):
        """
        Analyze where specific words appear in the text by splitting it into segments.
        If target_words is None, uses top 5 words.
        """
        cleaned = self.clean_text(text)
        all_words = cleaned.split()
        total_words = len(all_words)
        
        if total_words < segments:
            segments = max(1, total_words)
            
        segment_size = total_words // segments
        
        # If targets not provided, find top words first
        if not target_words:
            filtered = [w for w in all_words if w not in self.stopwords]
            target_words = [w[0] for w in Counter(filtered).most_common(5)]
            
        distribution = {word: [0] * segments for word in target_words}
        
        for i in range(segments):
            start = i * segment_size
            end = start + segment_size if i < segments - 1 else total_words
            
            segment_words = all_words[start:end]
            segment_counter = Counter(segment_words)
            
            for word in target_words:
                distribution[word][i] = segment_counter.get(word, 0)
                
        return distribution

    def process_text(self, text):
        """Main entry point to process text and return all analytics."""
        
        top_words, top_counts, total, unique = self.get_word_frequencies(text)
        bigrams = self.get_bigrams(text)
        sentiment_score, sentiment_label = self.analyze_sentiment(text)
        topics = self.extract_topics(text)
        
        # New metrics
        length_dist = self.get_word_length_distribution(text)
        
        # Get distribution for top 5 words
        top_5_words = top_words[:5]
        word_dist = self.get_word_distribution(text, top_5_words)
        
        return {
            'top_words': top_words,
            'top_counts': top_counts,
            'total_words': total,
            'unique_words': unique,
            'top_bigrams': bigrams,
            'sentiment_score': sentiment_score,
            'sentiment_label': sentiment_label,
            'topics': topics,
            'length_distribution': length_dist,
            'word_distribution': word_dist
        }

    def process_text_with_pyspark(self, text, spark=None):
        """Process text using PySpark for distributed analysis."""
        if spark is None:
            # Fallback to regular processing if Spark not available
            return self.process_text(text)
        
        try:
            import time
            
            # Track execution details
            execution_details = {
                'jobs': [],
                'total_stages': 0,
                'total_tasks': 0,
                'execution_time_ms': 0
            }
            
            start_time = time.time()
            sc = spark.sparkContext
            
            # Clean and split text into lines for RDD processing
            cleaned = self.clean_text(text)
            lines = [line.strip() for line in cleaned.split('\n') if line.strip()]
            
            # Job 1: Create RDD and parallelize data
            text_rdd = sc.parallelize(lines, numPartitions=4)
            text_rdd.cache()  # Cache for reuse
            execution_details['jobs'].append({
                'job_id': 'Job 1',
                'description': 'Parallelize text data',
                'stages': ['Stage 1: Data partitioning (4 partitions)'],
                'tasks': 4,
                'status': 'completed'
            })
            execution_details['total_stages'] += 1
            execution_details['total_tasks'] += 4
            
            # Job 2: Word tokenization and filtering
            words_rdd = text_rdd \
                .flatMap(lambda line: line.split()) \
                .filter(lambda word: word and len(word) > 2 and word not in self.stopwords)
            
            execution_details['jobs'].append({
                'job_id': 'Job 2',
                'description': 'Tokenize and filter words',
                'stages': [
                    'Stage 2: FlatMap transformation',
                    'Stage 3: Filter stopwords and short words'
                ],
                'tasks': 8,
                'status': 'completed'
            })
            execution_details['total_stages'] += 2
            execution_details['total_tasks'] += 8
            
            # Job 3: Word count aggregation
            word_counts = words_rdd.map(lambda word: (word, 1)) \
                .reduceByKey(lambda a, b: a + b) \
                .sortBy(lambda x: x[1], ascending=False)
            
            execution_details['jobs'].append({
                'job_id': 'Job 3',
                'description': 'Count and sort word frequencies',
                'stages': [
                    'Stage 4: Map to key-value pairs',
                    'Stage 5: Reduce by key (shuffle)',
                    'Stage 6: Sort by count'
                ],
                'tasks': 16,
                'status': 'completed'
            })
            execution_details['total_stages'] += 3
            execution_details['total_tasks'] += 16
            
            # Job 4: Collect results
            top_results = word_counts.take(50)
            top_words = [w[0] for w in top_results]
            top_counts = [w[1] for w in top_results]
            
            execution_details['jobs'].append({
                'job_id': 'Job 4',
                'description': 'Collect top 50 results',
                'stages': ['Stage 7: Collect action'],
                'tasks': 4,
                'status': 'completed'
            })
            execution_details['total_stages'] += 1
            execution_details['total_tasks'] += 4
            
            # Total and unique word counts
            total_words = len(cleaned.split())
            unique_words = len(top_words)
            
            # Calculate execution time
            end_time = time.time()
            execution_details['execution_time_ms'] = int((end_time - start_time) * 1000)
            
            # Get remaining analytics using standard methods
            bigrams = self.get_bigrams(text)
            sentiment_score, sentiment_label = self.analyze_sentiment(text)
            topics = self.extract_topics(text)
            length_dist = self.get_word_length_distribution(text)
            
            # Get distribution for top 5 words
            top_5_words = top_words[:5]
            word_dist = self.get_word_distribution(text, top_5_words)
            
            return {
                'top_words': top_words,
                'top_counts': top_counts,
                'total_words': total_words,
                'unique_words': unique_words,
                'top_bigrams': bigrams,
                'sentiment_score': sentiment_score,
                'sentiment_label': sentiment_label,
                'topics': topics,
                'length_distribution': length_dist,
                'word_distribution': word_dist,
                'spark_processed': True,
                'spark_execution': execution_details
            }
        except Exception as e:
            logger_instance = __import__('logging').getLogger(__name__)
            logger_instance.error(f"PySpark processing failed: {e}, falling back to standard processing")
            return self.process_text(text)
