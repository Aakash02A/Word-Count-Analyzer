import re
from flask import Flask, request, jsonify, send_file, render_template
import os
import json
import csv
from datetime import datetime
from collections import Counter
import requests
from docx import Document
from PyPDF2 import PdfReader
import pyspark_analyzer

# Initialize global variables for PySpark components
SparkSession = None
split = None
explode = None
lower = None
col = None
SPARK_AVAILABLE = False
spark_session = None
last_spark_job_runtime = None
recorded_spark_jobs = set()

# Try to import PySpark
try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import split, explode, lower, col
    SPARK_AVAILABLE = True
    print("PySpark is available and will be used for text analysis")
except ImportError:
    SPARK_AVAILABLE = False
    print("PySpark not available, using basic Python implementation")

# --- Flask Setup ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
app.config['HISTORY_FILE'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Utility Functions ---
def load_history():
    """Load analysis history from JSON file"""
    if os.path.exists(app.config['HISTORY_FILE']):
        with open(app.config['HISTORY_FILE'], "r") as f:
            return json.load(f)
    return []

def extract_text_from_file(filepath, file_extension):
    """Extract text content from different file types"""
    if file_extension == '.txt':
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    elif file_extension == '.docx':
        doc = Document(filepath)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    elif file_extension == '.pdf':
        reader = PdfReader(filepath)
        text = ''
        for page in reader.pages:
            text += page.extract_text() + '\n'
        return text
    elif file_extension == '.csv':
        # Read CSV using csv module and flatten to a whitespace-separated string
        try:
            with open(filepath, 'r', encoding='utf-8', newline='', errors='ignore') as csvfile:
                reader = csv.reader(csvfile)
                rows = []
                for row in reader:
                    rows.append(' '.join(str(cell) for cell in row if cell))
                return '\n'.join(rows)
        except Exception:
            # Fallback if any error
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    elif file_extension == '.html' or file_extension == '.htm':
        # Strip HTML tags to plain text
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            raw = f.read()
        # Remove script/style blocks and tags
        raw = re.sub(r'<script[\s\S]*?</script>', ' ', raw, flags=re.IGNORECASE)
        raw = re.sub(r'<style[\s\S]*?</style>', ' ', raw, flags=re.IGNORECASE)
        text_only = re.sub(r'<[^>]+>', ' ', raw)
        return re.sub(r'\s+', ' ', text_only)
    else:
        # Fallback for unknown file types
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

def save_history(history):
    """Save updated history list"""
    with open(app.config['HISTORY_FILE'], "w") as f:
        json.dump(history, f, indent=2)

def clean_text(text, stopwords):
    """Preprocess text: remove punctuation, lowercase, and apply stopwords"""
    text = re.sub(r'[^A-Za-z\s]', '', text).lower()
    words = [w for w in text.split() if w and w not in stopwords]
    return words

def clean_text_all_words(text):
    """Preprocess text: remove punctuation, lowercase, but don't apply stopwords"""
    text = re.sub(r'[^A-Za-z\s]', '', text).lower()
    words = [w for w in text.split() if w]  # Don't filter by stopwords here
    return words

def spark_word_count(text, stopwords=set()):
    """
    Word count implementation using PySpark.
    Falls back to simple implementation if PySpark is not available or fails.
    """
    if not SPARK_AVAILABLE:
        all_words = clean_text_all_words(text)
        filtered_words = [w for w in all_words if w not in stopwords]
        return all_words, filtered_words
    try:
        global spark_session
        if spark_session is None:
            # If session not started by user, fall back to python implementation
            all_words = clean_text_all_words(text)
            filtered_words = [w for w in all_words if w not in stopwords]
            return all_words, filtered_words
            
        # Use PySpark for word counting with DataFrame API
        from pyspark.sql.functions import split, explode, lower, col
        
        # Create DataFrame with the text
        text_df = spark_session.createDataFrame([(text,)], ["content"])
        
        # Preprocess text: convert to lowercase and split into words
        words_df = text_df.select(
            explode(
                split(
                    lower(col("content")), 
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
        filtered_words = [row["word"] for row in word_counts]
        
        # For all words (without stopwords filtering)
        all_word_counts_df = words_df.groupBy("word").count().orderBy(col("count").desc())
        all_word_counts = all_word_counts_df.collect()
        all_words = [row["word"] for row in all_word_counts]
        
        return all_words, filtered_words
    except Exception as e:
        print(f"PySpark word count fallback due to error: {e}")
        all_words = clean_text_all_words(text)
        filtered_words = [w for w in all_words if w not in stopwords]
        return all_words, filtered_words

# --- Routes ---
@app.route('/')
def home():
    """Serve the main dashboard UI"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handle uploaded file, analyze text, return word frequency data"""
    try:
        # Validate file
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
            
        file = request.files['file']
        if not file or not file.filename:
            return jsonify({"error": "No file selected"}), 400

        # Check file extension
        allowed_extensions = {'.txt', '.docx', '.pdf', '.csv', '.html', '.htm'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            return jsonify({"error": "Please upload TXT, DOCX, PDF, CSV, or HTML file"}), 400

        # Get stopwords
        stopwords_raw = request.form.get('stopwords', '')
        stopwords = set(w.strip().lower() for w in stopwords_raw.split(',') if w.strip())
        
        # Create a safe filename
        filename = file.filename
        safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Save uploaded file
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
            file.save(filepath)
        except Exception as e:
            app.logger.error(f"File save error: {str(e)}")
            return jsonify({"error": "Could not save the uploaded file"}), 500

        # Read text based on file type
        try:
            text = extract_text_from_file(filepath, file_extension)
        except Exception as e:
            app.logger.error(f"File read error: {str(e)}")
            return jsonify({"error": "Could not read the uploaded file"}), 500

        if not text.strip():
            return jsonify({"error": "The uploaded file is empty"}), 400

        try:
            # Get all words (without stopwords filtering) for the complete word list
            # Use PySpark if available and session is active, otherwise fall back to simple implementation
            if SPARK_AVAILABLE and spark_session is not None and pyspark_analyzer.is_pyspark_available():
                # Create a temporary file for PySpark analysis
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
                    temp_file.write(text)
                    temp_filepath = temp_file.name
                
                try:
                    # Use our dedicated PySpark analyzer for file-based analysis
                    all_words, filtered_words = pyspark_analyzer.analyze_text_with_pyspark(temp_filepath, stopwords)
                finally:
                    # Clean up temporary file
                    os.unlink(temp_filepath)
                
                # Create counters from the results
                all_counter = Counter(all_words)
                filtered_counter = Counter(filtered_words)
                if len(filtered_counter) == 0:
                    return jsonify({"error": "No valid words found in the text"}), 400
            else:
                # Use the text-based approach
                all_words = clean_text_all_words(text)
                all_counter = Counter(all_words)
                
                # Get filtered words (with stopwords) for the top words chart
                filtered_words = clean_text(text, stopwords)
                if not filtered_words and stopwords:
                    return jsonify({"error": "No valid words found after removing punctuation and stopwords"}), 400

                filtered_counter = Counter(filtered_words)
                if len(filtered_counter) == 0:
                    return jsonify({"error": "No valid words found in the text"}), 400

            # Get top words (filtered by stopwords)
            top = filtered_counter.most_common(15)
            if not top:
                return jsonify({"error": "Could not analyze word frequency"}), 400
                
            top_words, top_counts = zip(*top)
            
            # Convert tuples to lists for JSON serialization
            top_words = list(top_words)
            top_counts = list(top_counts)
            
            # Prepare complete word list (all words with counts)
            all_words_list = list(all_counter.keys())
            all_counts_list = list(all_counter.values())

            # Save results
            # Basic consistency checks before persisting
            if len(all_words_list) != len(all_counts_list):
                msg = f"Inconsistent word/count lengths: words={len(all_words_list)} counts={len(all_counts_list)}"
                app.logger.error(msg)
                return jsonify({"error": msg}), 500

            # Store in history
            try:
                history = load_history()
                source_type = "pyspark" if SPARK_AVAILABLE and spark_session is not None else "file"
                spark_ui_url = None
                job_id = None
                if source_type == "pyspark":
                    try:
                        spark_ui_url = spark_session.sparkContext.uiWebUrl
                        tracker = spark_session.sparkContext.statusTracker()
                        completed = tracker.getCompletedJobIds()
                        if completed:
                            job_id = completed[-1]
                    except Exception:
                        pass
                record = {
                    "id": len(history) + 1,
                    "filename": safe_filename,
                    "stored_at": datetime.now().isoformat(),
                    "source": source_type,
                    "status": "completed",
                    "top_words": top_words,
                    "top_counts": top_counts,
                    "all_words": all_words_list,
                    "all_counts": all_counts_list,
                    "total_words": len(all_words),
                    "unique_words": len(all_counter),
                    "stopwords": list(stopwords) if stopwords else [],
                    "processing_time": "< 1s",
                    "spark_ui": spark_ui_url,
                    "spark_job_id": job_id
                }
                history.append(record)
                save_history(history)
            except Exception as e:
                app.logger.error(f"Error saving history: {e}")
                return jsonify({"error": f"Error saving history: {e}"}), 500

            # Save CSV file for download (with all words)
            try:
                csv_name = f"{os.path.splitext(safe_filename)[0]}_analysis.csv"
                csv_path = os.path.join(app.config['UPLOAD_FOLDER'], csv_name)
                with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Word', 'Count'])
                    for word, count in zip(all_words_list, all_counts_list):
                        writer.writerow([word, count])
            except Exception as e:
                app.logger.error(f"Error writing CSV file: {e}")
                return jsonify({"error": f"Error writing CSV file: {e}"}), 500

            # Return response
            return jsonify({
                "top_words": top_words,
                "top_counts": top_counts,
                "all_words": all_words_list,
                "all_counts": all_counts_list,
                "filename": safe_filename,
                "total_words": len(all_words),
                "unique_words": len(all_counter),
                "csv_download": f"/download/{csv_name}"
            })

        except Exception as e:
            app.logger.error(f"Text processing error: {str(e)}")
            return jsonify({"error": "Error processing the text content"}), 500

    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Compatibility endpoint: forward to existing /analyze handler."""
    return analyze()

@app.route('/download/<filename>')
def download_file(filename):
    """Allow users to download analyzed CSV file"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

@app.route('/list_history')
def list_history():
    """Return the full history list"""
    history = load_history()
    history.sort(key=lambda x: x['stored_at'], reverse=True)
    return jsonify(history)

@app.route('/history_detail/<int:hid>')
def history_detail(hid):
    """Return specific analysis details by ID"""
    history = load_history()
    for h in history:
        if h['id'] == hid:
            return jsonify(h)
    return jsonify({"error": "History not found"}), 404

@app.route('/analyze_url', methods=['POST'])
def analyze_url():
    """Analyze text content from a URL"""
    try:
        # Get URL from form data
        url = request.form.get('url')
        if not url:
            return jsonify({"error": "No URL provided"}), 400
            
        # Get stopwords
        stopwords_raw = request.form.get('stopwords', '')
        stopwords = set(w.strip().lower() for w in stopwords_raw.split(',') if w.strip())
        
        # Fetch content from URL
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            text = response.text
        except requests.RequestException as e:
            return jsonify({"error": f"Could not fetch content from URL: {str(e)}"}), 400
        
        if not text.strip():
            return jsonify({"error": "The URL content is empty"}), 400

        try:
            # Get all words (without stopwords filtering) for the complete word list
            all_words = clean_text_all_words(text)
            all_counter = Counter(all_words)
            
            # Get filtered words (with stopwords) for the top words chart
            filtered_words = clean_text(text, stopwords)
            if not filtered_words and stopwords:
                return jsonify({"error": "No valid words found after removing punctuation and stopwords"}), 400

            filtered_counter = Counter(filtered_words)
            if len(filtered_counter) == 0:
                return jsonify({"error": "No valid words found in the text"}), 400

            # Get top words (filtered by stopwords)
            top = filtered_counter.most_common(15)
            if not top:
                return jsonify({"error": "Could not analyze word frequency"}), 400
                
            top_words, top_counts = zip(*top)
            
            # Convert tuples to lists for JSON serialization
            top_words = list(top_words)
            top_counts = list(top_counts)
            
            # Prepare complete word list (all words with counts)
            all_words_list = list(all_counter.keys())
            all_counts_list = list(all_counter.values())

            # Store in history
            try:
                history = load_history()
                source_type = "pyspark" if SPARK_AVAILABLE and spark_session is not None else "url"
                spark_ui_url = None
                job_id = None
                if source_type == "pyspark":
                    try:
                        spark_ui_url = spark_session.sparkContext.uiWebUrl
                        tracker = spark_session.sparkContext.statusTracker()
                        completed = tracker.getCompletedJobIds()
                        if completed:
                            job_id = completed[-1]
                    except Exception:
                        pass
                record = {
                    "id": len(history) + 1,
                    "filename": url,
                    "stored_at": datetime.now().isoformat(),
                    "source": source_type,
                    "status": "completed",
                    "top_words": top_words,
                    "top_counts": top_counts,
                    "all_words": all_words_list,
                    "all_counts": all_counts_list,
                    "total_words": len(all_words),
                    "unique_words": len(all_counter),
                    "stopwords": list(stopwords) if stopwords else [],
                    "processing_time": "< 1s",
                    "spark_ui": spark_ui_url,
                    "spark_job_id": job_id
                }
                history.append(record)
                save_history(history)
            except Exception as e:
                app.logger.error(f"Error saving history: {e}")

            # Return results
            return jsonify({
                "top_words": top_words,
                "top_counts": top_counts,
                "all_words": all_words_list,
                "all_counts": all_counts_list,
                "filename": url,
                "total_words": len(all_words),
                "unique_words": len(all_counter)
            })
            
        except Exception as e:
            app.logger.error(f"Text processing error: {str(e)}")
            return jsonify({"error": "Error processing the text content"}), 500

    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@app.route('/api/update_analysis', methods=['POST'])
def update_analysis():
    """Update analysis with new stopwords without re-uploading the file"""
    try:
        # Get filename and stopwords from form data
        filename = request.form.get('filename')
        stopwords_raw = request.form.get('stopwords', '')
        stopwords = set(w.strip().lower() for w in stopwords_raw.split(',') if w.strip())
        
        if not filename:
            return jsonify({"error": "No filename provided"}), 400
            
        # Check if file exists
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404
            
        # Read text based on file type
        try:
            file_extension = os.path.splitext(filename)[1].lower()
            text = extract_text_from_file(filepath, file_extension)
        except Exception as e:
            app.logger.error(f"File read error: {str(e)}")
            return jsonify({"error": "Could not read the file"}), 500

        if not text.strip():
            return jsonify({"error": "The file is empty"}), 400

        try:
            # Get all words (without stopwords filtering) for the complete word list
            all_words = clean_text_all_words(text)
            all_counter = Counter(all_words)
            
            # Get filtered words (with stopwords) for the top words chart
            filtered_words = clean_text(text, stopwords)
            if not filtered_words and stopwords:
                return jsonify({"error": "No valid words found after removing punctuation and stopwords"}), 400

            filtered_counter = Counter(filtered_words)
            if len(filtered_counter) == 0:
                return jsonify({"error": "No valid words found in the text"}), 400

            # Get top words (filtered by stopwords)
            top = filtered_counter.most_common(15)
            if not top:
                return jsonify({"error": "Could not analyze word frequency"}), 400
                
            top_words, top_counts = zip(*top)
            
            # Convert tuples to lists for JSON serialization
            top_words = list(top_words)
            top_counts = list(top_counts)
            
            # Prepare complete word list (all words with counts)
            all_words_list = list(all_counter.keys())
            all_counts_list = list(all_counter.values())

            # Return updated results
            return jsonify({
                "top_words": top_words,
                "top_counts": top_counts,
                "all_words": all_words_list,
                "all_counts": all_counts_list,
                "filename": filename,
                "total_words": len(all_words),
                "unique_words": len(all_counter)
            })
            
        except Exception as e:
            app.logger.error(f"Text processing error: {str(e)}")
            return jsonify({"error": "Error processing the text content"}), 500

    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get all history records"""
    try:
        history = load_history()
        return jsonify(history)
    except Exception as e:
        app.logger.error(f"Error loading history: {str(e)}")
        return jsonify({"error": "Failed to load history"}), 500

@app.route('/api/history/<int:record_id>', methods=['DELETE'])
def delete_history_record(record_id):
    """Delete a specific history record"""
    try:
        history = load_history()
        # Find and remove the record
        updated_history = [r for r in history if r.get('id') != record_id]
        
        if len(updated_history) == len(history):
            return jsonify({"error": "Record not found"}), 404
        
        save_history(updated_history)
        return jsonify({"success": True, "message": "Record deleted successfully"})
    except Exception as e:
        app.logger.error(f"Error deleting history record: {str(e)}")
        return jsonify({"error": "Failed to delete record"}), 500

# --- Spark Management Endpoints ---
@app.route('/api/spark/start', methods=['POST'])
def spark_start():
    if not SPARK_AVAILABLE:
        return jsonify({"error": "PySpark not available in this environment"}), 400
    # Validate Java availability for Spark on Windows
    java_home = os.environ.get('JAVA_HOME')
    if os.name == 'nt' and not java_home:
        return jsonify({
            "error": "JAVA_HOME is not set. Install Java (JDK) and set JAVA_HOME to enable Spark.",
            "hint": "Example: setx JAVA_HOME \"C:\\Program Files\\Java\\jdk-17\""
        }), 400
    global spark_session
    if spark_session is not None:
        try:
            if not spark_session.sparkContext._jsc.sc().isStopped():
                return jsonify({"message": "Spark session already active"})
        except Exception:
            pass
    try:
        spark_session = SparkSession.builder.appName("WordIntelligence").getOrCreate()
        return jsonify({"message": "Spark session started", "spark_ui_url": spark_session.sparkContext.uiWebUrl})
    except Exception as e:
        app.logger.error(f"Spark start error: {e}")
        return jsonify({"error": f"Failed to start Spark: {e}"}), 500

@app.route('/api/spark/stop', methods=['POST'])
def spark_stop():
    global spark_session
    if spark_session is None:
        return jsonify({"message": "No active Spark session"})
    try:
        spark_session.stop()
        spark_session = None
        return jsonify({"message": "Spark session stopped"})
    except Exception as e:
        app.logger.error(f"Spark stop error: {e}")
        return jsonify({"error": f"Failed to stop Spark: {e}"}), 500

@app.route('/api/spark/status', methods=['GET'])
def spark_status():
    if not SPARK_AVAILABLE:
        return jsonify({
            "available": False,
            "active": False,
            "running_jobs": 0,
            "completed_jobs": 0,
            "executor_memory": None,
            "last_job_runtime": last_spark_job_runtime,
            "spark_ui_url": None
        })
    global spark_session
    active = False
    running_jobs = 0
    completed_jobs = 0
    executor_memory = None
    spark_ui_url = None
    try:
        if spark_session is not None:
            sc = spark_session.sparkContext
            spark_ui_url = sc.uiWebUrl
            tracker = sc.statusTracker()
            running_jobs = len(tracker.getActiveJobIds())
            completed_jobs = len(tracker.getCompletedJobIds())
            # Memory status (total - remaining across executors)
            try:
                mem_status = sc._jsc.sc().getExecutorMemoryStatus().entrySet()
                total = 0
                used = 0
                for entry in mem_status:
                    host = entry.getKey()
                    vals = entry.getValue()
                    host_total = int(vals._1()) if hasattr(vals, '_1') else int(vals[0])
                    host_remaining = int(vals._2()) if hasattr(vals, '_2') else int(vals[1])
                    total += host_total
                    used += (host_total - host_remaining)
                if total > 0:
                    executor_memory = f"{used/1024/1024:.1f}MB / {total/1024/1024:.1f}MB"
            except Exception:
                executor_memory = None
            active = True
    except Exception as e:
        app.logger.error(f"Spark status error: {e}")
    return jsonify({
        "available": True,
        "active": active,
        "running_jobs": running_jobs,
        "completed_jobs": completed_jobs,
        "executor_memory": executor_memory,
        "last_job_runtime": last_spark_job_runtime,
        "spark_ui_url": spark_ui_url
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Simple health check endpoint for end-to-end tests."""
    try:
        return jsonify({
            "status": "ok",
            "spark_available": SPARK_AVAILABLE
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Disable debug to improve Spark session stability
    app.run(debug=False)