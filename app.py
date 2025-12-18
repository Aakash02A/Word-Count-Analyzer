from flask import Flask, render_template, request, jsonify, send_file
import os
import io
import csv
import logging
from datetime import datetime
import threading
import time
import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import split, explode, lower, regexp_replace, col, count

# Import helper modules
import database as db
from text_analyzer import TextAnalyzer
from pypdf import PdfReader
import docx

# Initialize App
app = Flask(__name__)
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Analyzer
analyzer = TextAnalyzer()

# Initialize DB
db.init_db()

# Initialize Spark Session with proper configuration
spark = None
ENABLE_PYSPARK = os.environ.get('ENABLE_PYSPARK', 'False').lower() == 'true'  # Disabled by default

# To enable PySpark and Spark UI:
# 1. Set environment variable: ENABLE_PYSPARK=True
# 2. Ensure PySpark is installed: pip install pyspark
# 3. Run the application: python app.py
# 4. Upload a file to start Spark processing
# 5. Spark UI will be automatically available at: http://localhost:4040
# 6. Use the "Spark UI" panel in the app to:
#    - Check Spark UI availability status
#    - Click "Open Application UI" to open http://localhost:4040 in a new tab
#    - Use quick access buttons to open specific Spark UI pages (Jobs, Stages, Executors, etc.)
#    - View real-time Spark metrics and execution details
# Note: The app connects directly to the real Spark UI (no simulated template)

def initialize_spark():
    """Initialize PySpark with proper configuration"""
    try:
        from pyspark import SparkConf
        
        conf = SparkConf()
        conf.setAppName("WordCountAnalyzer")
        conf.setMaster("local[*]")  # Use all available cores
        conf.set("spark.driver.memory", "1g")
        conf.set("spark.executor.memory", "1g")
        conf.set("spark.sql.shuffle.partitions", "4")
        conf.set("spark.ui.enabled", "true")
        conf.set("spark.ui.port", "4040")
        conf.set("spark.driver.host", "localhost")
        conf.set("spark.sql.warehouse.dir", os.path.join(os.getcwd(), "spark-warehouse"))
        
        session = SparkSession.builder.config(conf=conf).getOrCreate()
        session.sparkContext.setLogLevel("WARN")
        logger.info("✓ PySpark initialized successfully on local[*]")
        return session
    except Exception as e:
        logger.warning(f"⚠ PySpark initialization failed: {e}")
        logger.info("→ Falling back to standard processing")
        return None

if ENABLE_PYSPARK:
    spark = initialize_spark()
else:
    logger.info("PySpark disabled (set ENABLE_PYSPARK=True to enable)")

# Spark State (Simulated for this MVP)
spark_state = {
    'status': 'idle', # idle, running, completed, error
    'progress': 0,
    'job_id': None,
    'metrics': {
        'jobs': 0,
        'stages': 0,
        'tasks': 0,
        'memory': 0,
        'shuffle_read': 0,
        'shuffle_write': 0,
        'task_time': 0,
        'skew': 'Low'
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        content = ""
        filename = file.filename.lower()
        
        # Update spark state - analysis starting
        global spark_state
        spark_state['status'] = 'running'
        spark_state['progress'] = 0
        spark_state['job_id'] = 'job_' + datetime.now().strftime('%M%S%f')
        
        # Determine file type and extract text
        spark_state['progress'] = 20
        if filename.endswith('.pdf'):
            try:
                reader = PdfReader(file)
                text = []
                for page in reader.pages:
                    text.append(page.extract_text() or "")
                content = "\n".join(text)
            except Exception as e:
                logger.error(f"Error parsing PDF: {e}")
                spark_state['status'] = 'error'
                return jsonify({'error': 'Failed to read PDF file'}), 400
                
        elif filename.endswith('.docx'):
            try:
                doc = docx.Document(file)
                text = []
                for para in doc.paragraphs:
                    text.append(para.text)
                content = "\n".join(text)
            except Exception as e:
                logger.error(f"Error parsing DOCX: {e}")
                spark_state['status'] = 'error'
                return jsonify({'error': 'Failed to read DOCX file'}), 400
                
        else:
            # Basic text file fallback
            try:
                content = file.read().decode('utf-8')
            except UnicodeDecodeError:
                file.seek(0)
                content = file.read().decode('latin-1')
        
        if not content.strip():
            spark_state['status'] = 'error'
            return jsonify({'error': 'File is empty or text could not be extracted'}), 400

        # Process Content with PySpark
        spark_state['progress'] = 40
        if spark is not None:
            results = analyzer.process_text_with_pyspark(content, spark)
        else:
            results = analyzer.process_text(content)
        
        spark_state['progress'] = 80
        
        # Add metadata for DB
        results['source'] = 'file'
        results['filename'] = file.filename
        
        # Save to DB
        record_id = db.add_analysis_record(results)
        results['analysis_id'] = record_id
        
        spark_state['progress'] = 100
        spark_state['status'] = 'completed'
        
        return jsonify(results)

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        spark_state['status'] = 'error'
        return jsonify({'error': str(e)}), 500

@app.route('/analyze_url', methods=['POST'])
def analyze_url():
    url = request.form.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400
        
    try:
        global spark_state
        spark_state['status'] = 'running'
        spark_state['progress'] = 0
        spark_state['job_id'] = 'job_' + datetime.now().strftime('%M%S%f')
        
        # Fetch content
        spark_state['progress'] = 30
        content = analyzer.fetch_url_content(url)
        
        if not content:
            spark_state['status'] = 'error'
            return jsonify({'error': 'No content found at URL'}), 400
            
        # Process Content with PySpark
        spark_state['progress'] = 60
        if spark is not None:
            results = analyzer.process_text_with_pyspark(content, spark)
        else:
            results = analyzer.process_text(content)
        
        spark_state['progress'] = 90
        
        # Add metadata for DB
        results['source'] = 'url'
        results['filename'] = url
        
        # Save to DB
        record_id = db.add_analysis_record(results)
        results['analysis_id'] = record_id
        
        spark_state['progress'] = 100
        spark_state['status'] = 'completed'
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"URL Analysis failed: {e}")
        spark_state['status'] = 'error'
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/stats')
def get_stats():
    stats = db.get_dashboard_stats()
    return jsonify(stats)

@app.route('/api/history', methods=['GET'])
def get_history():
    history = db.get_all_history()
    return jsonify(history)

@app.route('/api/history/<int:record_id>', methods=['GET'])
def get_history_detail(record_id):
    record = db.get_record_by_id(record_id)
    if record:
        return jsonify(record)
    return jsonify({'error': 'Record not found'}), 404

@app.route('/api/history/<int:record_id>', methods=['DELETE'])
def delete_history_item(record_id):
    db.delete_record(record_id)
    return jsonify({'status': 'success'})

@app.route('/download/analysis_<int:record_id>_results.csv')
def download_csv(record_id):
    record = db.get_record_by_id(record_id)
    if not record:
        return "Record not found", 404
        
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers / metadata at top
    writer.writerow(['Analysis ID', record['id']])
    writer.writerow(['Source', record['source']])
    writer.writerow(['Filename/URL', record['filename']])
    writer.writerow(['Date', record['created_at']])
    writer.writerow(['Total Words', record['total_words']])
    writer.writerow(['Unique Words', record['unique_words']])
    writer.writerow(['Sentiment', record['sentiment_label']])
    writer.writerow([])
    
    # Write Word Frequencies
    writer.writerow(['Word', 'Frequency'])
    words = record['top_words']
    counts = record['top_counts']
    
    # Zip them together. If counts are missing, defaults to empty list from DB helper
    for i, word in enumerate(words):
        freq = counts[i] if i < len(counts) else '?'
        writer.writerow([word, freq])

    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f"analysis_{record_id}.csv"
    )

import threading
import time

# Spark Routes (Simulated)
@app.route('/api/spark/start', methods=['POST'])
def start_spark():
    global spark_state
    
    if spark_state['status'] == 'running':
        return jsonify({'status': 'already_running', 'job_id': spark_state['job_id']})

    spark_state['status'] = 'running'
    spark_state['progress'] = 0
    spark_state['job_id'] = 'job_' + datetime.now().strftime('%M%S')
    # Reset metrics
    spark_state['metrics'] = {
        'jobs': 0,
        'stages': 0,
        'tasks': 0,
        'memory': 0,
        'shuffle_read': 0,
        'shuffle_write': 0,
        'task_time': 0,
        'skew': 'Low'
    }
    
    # Start background simulation
    def simulate_job():
        import random
        for i in range(1, 101):
            if spark_state['status'] != 'running':
                break
            
            spark_state['progress'] = i
            
            # Simulate accumulating metrics
            metrics = spark_state['metrics']
            if i % 10 == 0:
                metrics['jobs'] += 1
                metrics['stages'] += random.randint(1, 2)
            
            metrics['tasks'] += random.randint(5, 15)
            metrics['memory'] = int(metrics['memory'] + random.uniform(50, 200)) # MB
            metrics['shuffle_read'] = int(metrics['shuffle_read'] + random.uniform(10, 50))
            metrics['shuffle_write'] = int(metrics['shuffle_write'] + random.uniform(5, 30))
            metrics['task_time'] = int(metrics['task_time'] + random.uniform(1, 5)) # ms avg adjustment
            
            time.sleep(0.1) # Total 10 seconds
        
        if spark_state['status'] == 'running':
            spark_state['status'] = 'completed'

    thread = threading.Thread(target=simulate_job)
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started', 'job_id': spark_state['job_id']})

@app.route('/api/spark/stop', methods=['POST'])
def stop_spark():
    global spark_state
    spark_state['status'] = 'idle'
    spark_state['progress'] = 0
    return jsonify({'status': 'stopped'})

@app.route('/api/spark/status')
def spark_status():
    return jsonify(spark_state)

@app.route('/api/spark/ui_status')
def spark_ui_status():
    """Check if Spark UI is accessible on port 4040"""
    import socket
    try:
        # Check if port 4040 is open (Spark UI running)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 4040))
        sock.close()
        
        is_available = result == 0
        return jsonify({
            'available': is_available,
            'url': 'http://localhost:4040' if is_available else None,
            'spark_enabled': ENABLE_PYSPARK,
            'spark_initialized': spark is not None
        })
    except Exception as e:
        return jsonify({
            'available': False,
            'url': None,
            'spark_enabled': ENABLE_PYSPARK,
            'spark_initialized': spark is not None,
            'error': str(e)
        })


# ==========================================
# Secondary Flask App for Spark UI (Port 4040)
# ==========================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Disable reloader when using PySpark to avoid re-initialization issues
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
