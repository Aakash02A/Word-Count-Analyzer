# File 1: app.py (Main Flask Application)
import os
import json
import uuid
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import requests
from bs4 import BeautifulSoup
from pyspark_analyzer import PySparkAnalyzer
from spark_ui import SparkUIManager
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ANALYSIS_RESULTS'] = 'analysis_results'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'docx', 'csv', 'html', 'htm'}
app.config['SPARK_MASTER'] = 'local[*]'
app.config['SPARK_APP_NAME'] = 'WordIntelligenceAnalytics'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['ANALYSIS_RESULTS'], exist_ok=True)

# Initialize PySpark Analyzer
spark_analyzer = PySparkAnalyzer(
    master=app.config['SPARK_MASTER'],
    app_name=app.config['SPARK_APP_NAME']
)

# Initialize Spark UI Manager
spark_ui_manager = SparkUIManager()

# In-memory storage for history (in production, use database)
analysis_history = []

class AnalysisResult:
    """Class to manage analysis results and history"""
    
    def __init__(self, analysis_id, analysis_type, filename=None, url=None):
        self.analysis_id = analysis_id
        self.analysis_type = analysis_type
        self.filename = filename
        self.url = url
        self.timestamp = datetime.now()
        self.status = 'pending'
        self.results = {}
        self.metrics = {}
        self.spark_job_id = None
        
    def to_dict(self):
        return {
            'id': self.analysis_id,
            'type': self.analysis_type,
            'filename': self.filename,
            'url': self.url,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'results': self.results,
            'metrics': self.metrics,
            'spark_job_id': self.spark_job_id
        }

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_file(filepath, file_type):
    """Extract text from different file formats"""
    try:
        if file_type == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_type == 'pdf':
            # PDF text extraction
            try:
                import PyPDF2
                with open(filepath, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    text = ''
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                    return text
            except ImportError:
                logger.warning("PyPDF2 not installed, using fallback")
                with open(filepath, 'rb') as f:
                    return f.read().decode('utf-8', errors='ignore')
        elif file_type in ['docx', 'doc']:
            # DOCX text extraction
            try:
                import docx
                doc = docx.Document(filepath)
                return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            except ImportError:
                logger.warning("python-docx not installed")
                raise Exception("DOCX processing requires python-docx library")
        elif file_type == 'csv':
            # CSV text extraction
            df = pd.read_csv(filepath)
            return ' '.join(df.astype(str).values.flatten())
        elif file_type in ['html', 'htm']:
            # HTML text extraction
            with open(filepath, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                return soup.get_text()
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    except Exception as e:
        logger.error(f"Error extracting text from {filepath}: {str(e)}")
        raise

def extract_text_from_url(url):
    """Extract text content from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        logger.error(f"Error extracting text from URL {url}: {str(e)}")
        raise

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'spark_status': spark_analyzer.check_spark_status(),
        'system': {
            'upload_folder': app.config['UPLOAD_FOLDER'],
            'analysis_folder': app.config['ANALYSIS_RESULTS']
        }
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and analysis"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Generate unique ID for this analysis
        analysis_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{analysis_id}_{filename}")
        
        # Save file
        file.save(file_path)
        logger.info(f"File saved: {file_path}")
        
        # Create analysis record
        analysis = AnalysisResult(analysis_id, 'file', filename=filename)
        analysis_history.append(analysis)
        
        # Extract text from file
        try:
            text_content = extract_text_from_file(file_path, file_extension)
            analysis.status = 'text_extracted'
        except Exception as e:
            analysis.status = 'failed'
            analysis.results = {'error': str(e)}
            return jsonify(analysis.to_dict()), 500
        
        # Analyze with PySpark
        try:
            analysis.status = 'analyzing'
            spark_results = spark_analyzer.analyze_text(text_content)
            
            # Update analysis results
            analysis.results = spark_results
            analysis.metrics = {
                'total_words': spark_results.get('total_words', 0),
                'unique_words': spark_results.get('unique_words', 0),
                'processing_time': spark_results.get('processing_time', 0),
                'vocabulary_richness': spark_results.get('vocabulary_richness', 0)
            }
            analysis.status = 'completed'
            analysis.spark_job_id = spark_results.get('job_id')
            
            # Save results to file
            result_file = os.path.join(
                app.config['ANALYSIS_RESULTS'], 
                f"{analysis_id}_results.json"
            )
            with open(result_file, 'w') as f:
                json.dump(analysis.to_dict(), f, indent=2, default=str)
            
            logger.info(f"Analysis completed: {analysis_id}")
            
            return jsonify(analysis.to_dict())
            
        except Exception as e:
            analysis.status = 'failed'
            analysis.results = {'error': str(e)}
            logger.error(f"Analysis failed: {str(e)}")
            return jsonify(analysis.to_dict()), 500
            
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/url', methods=['POST'])
def analyze_url():
    """Analyze text content from URL"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        analysis_id = str(uuid.uuid4())
        
        # Create analysis record
        analysis = AnalysisResult(analysis_id, 'url', url=url)
        analysis_history.append(analysis)
        
        # Extract text from URL
        try:
            text_content = extract_text_from_url(url)
            analysis.status = 'text_extracted'
        except Exception as e:
            analysis.status = 'failed'
            analysis.results = {'error': str(e)}
            return jsonify(analysis.to_dict()), 500
        
        # Analyze with PySpark
        try:
            analysis.status = 'analyzing'
            spark_results = spark_analyzer.analyze_text(text_content)
            
            # Update analysis results
            analysis.results = spark_results
            analysis.metrics = {
                'total_words': spark_results.get('total_words', 0),
                'unique_words': spark_results.get('unique_words', 0),
                'processing_time': spark_results.get('processing_time', 0),
                'vocabulary_richness': spark_results.get('vocabulary_richness', 0)
            }
            analysis.status = 'completed'
            analysis.spark_job_id = spark_results.get('job_id')
            
            # Save results
            result_file = os.path.join(
                app.config['ANALYSIS_RESULTS'], 
                f"{analysis_id}_results.json"
            )
            with open(result_file, 'w') as f:
                json.dump(analysis.to_dict(), f, indent=2, default=str)
            
            return jsonify(analysis.to_dict())
            
        except Exception as e:
            analysis.status = 'failed'
            analysis.results = {'error': str(e)}
            return jsonify(analysis.to_dict()), 500
            
    except Exception as e:
        logger.error(f"URL analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/<analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    """Get analysis results by ID"""
    try:
        # Look for analysis in history
        for analysis in analysis_history:
            if analysis.analysis_id == analysis_id:
                return jsonify(analysis.to_dict())
        
        # Check if results file exists
        result_file = os.path.join(
            app.config['ANALYSIS_RESULTS'], 
            f"{analysis_id}_results.json"
        )
        
        if os.path.exists(result_file):
            with open(result_file, 'r') as f:
                results = json.load(f)
            return jsonify(results)
        
        return jsonify({'error': 'Analysis not found'}), 404
        
    except Exception as e:
        logger.error(f"Error getting analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get analysis history with filtering"""
    try:
        # Get query parameters
        filter_type = request.args.get('type', 'all')
        search = request.args.get('search', '').lower()
        time_range = request.args.get('time_range', 'all')
        
        # Filter history
        filtered = []
        for analysis in analysis_history:
            # Type filter
            if filter_type != 'all' and analysis.analysis_type != filter_type:
                continue
            
            # Search filter
            if search:
                search_text = f"{analysis.filename or ''} {analysis.url or ''} {analysis.analysis_type}".lower()
                if search not in search_text:
                    continue
            
            # Time filter (simplified)
            if time_range != 'all':
                now = datetime.now()
                if time_range == 'today':
                    if analysis.timestamp.date() != now.date():
                        continue
                elif time_range == 'week':
                    days_diff = (now - analysis.timestamp).days
                    if days_diff > 7:
                        continue
                elif time_range == 'month':
                    days_diff = (now - analysis.timestamp).days
                    if days_diff > 30:
                        continue
            
            filtered.append(analysis.to_dict())
        
        # Sort by timestamp (newest first)
        filtered.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'total': len(filtered),
            'results': filtered
        })
        
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/csv/<analysis_id>', methods=['GET'])
def export_csv(analysis_id):
    """Export analysis results as CSV"""
    try:
        # Find analysis
        analysis = None
        for a in analysis_history:
            if a.analysis_id == analysis_id:
                analysis = a
                break
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        # Create CSV from word frequencies
        words = analysis.results.get('word_frequencies', [])
        
        if not words:
            return jsonify({'error': 'No word frequency data available'}), 400
        
        # Create DataFrame
        df = pd.DataFrame(words)
        
        # Save CSV
        csv_path = os.path.join(
            app.config['ANALYSIS_RESULTS'], 
            f"{analysis_id}_export.csv"
        )
        df.to_csv(csv_path, index=False)
        
        return send_file(
            csv_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"word_analysis_{analysis_id}.csv"
        )
        
    except Exception as e:
        logger.error(f"Error exporting CSV: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/spark/run', methods=['POST'])
def run_spark_job():
    """Run a Spark analysis job"""
    try:
        data = request.get_json()
        
        # Get text content or file path
        text_content = data.get('text', '')
        file_path = data.get('file_path', '')
        
        if not text_content and not file_path:
            return jsonify({'error': 'No text content or file path provided'}), 400
        
        # Create analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Run Spark analysis
        spark_results = spark_analyzer.analyze_text(text_content)
        
        # Create analysis record
        analysis = AnalysisResult(analysis_id, 'spark_job')
        analysis.results = spark_results
        analysis.status = 'completed'
        analysis.spark_job_id = spark_results.get('job_id')
        analysis_history.append(analysis)
        
        return jsonify({
            'analysis_id': analysis_id,
            'status': 'completed',
            'spark_job_id': analysis.spark_job_id,
            'results': spark_results
        })
        
    except Exception as e:
        logger.error(f"Spark job error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/spark/status', methods=['GET'])
def get_spark_status():
    """Get Spark cluster status and metrics"""
    try:
        status = spark_analyzer.check_spark_status()
        metrics = spark_analyzer.get_spark_metrics()
        
        return jsonify({
            'status': status,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting Spark status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/spark/ui/urls', methods=['GET'])
def get_spark_ui_urls():
    """Get Spark UI URLs"""
    try:
        urls = spark_ui_manager.get_spark_ui_urls()
        return jsonify(urls)
        
    except Exception as e:
        logger.error(f"Error getting Spark UI URLs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        total_analyses = len(analysis_history)
        file_analyses = len([a for a in analysis_history if a.analysis_type == 'file'])
        url_analyses = len([a for a in analysis_history if a.analysis_type == 'url'])
        
        # Calculate average processing time
        processing_times = []
        for analysis in analysis_history:
            if analysis.status == 'completed' and 'processing_time' in analysis.metrics:
                processing_times.append(analysis.metrics['processing_time'])
        
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        return jsonify({
            'total_analyses': total_analyses,
            'files_processed': file_analyses,
            'urls_analyzed': url_analyses,
            'avg_processing_time': round(avg_processing_time, 3),
            'spark_status': spark_analyzer.check_spark_status()
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/visualizations/data', methods=['GET'])
def get_visualization_data():
    """Get data for visualizations"""
    try:
        analysis_id = request.args.get('analysis_id')
        
        if analysis_id:
            # Get specific analysis
            for analysis in analysis_history:
                if analysis.analysis_id == analysis_id:
                    return jsonify(analysis.results)
        
        # Return sample/default data
        return jsonify({
            'word_frequencies': [],
            'bigrams': [],
            'trigrams': [],
            'sentiment_scores': {},
            'emotion_analysis': {},
            'topic_clusters': []
        })
        
    except Exception as e:
        logger.error(f"Error getting visualization data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/filter/stopwords', methods=['POST'])
def filter_stopwords():
    """Apply stopword filtering"""
    try:
        data = request.get_json()
        analysis_id = data.get('analysis_id')
        stopwords = data.get('stopwords', [])
        
        if not analysis_id:
            return jsonify({'error': 'Analysis ID is required'}), 400
        
        # Find analysis
        analysis = None
        for a in analysis_history:
            if a.analysis_id == analysis_id:
                analysis = a
                break
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        # Apply stopword filtering
        filtered_results = spark_analyzer.filter_stopwords(
            analysis.results.get('word_frequencies', []),
            stopwords
        )
        
        return jsonify({
            'filtered_count': len(filtered_results),
            'results': filtered_results[:100]  # Return top 100
        })
        
    except Exception as e:
        logger.error(f"Error filtering stopwords: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

def cleanup_old_files():
    """Clean up old files to prevent disk space issues"""
    import time
    current_time = time.time()
    max_age = 24 * 60 * 60  # 24 hours
    
    for folder in [app.config['UPLOAD_FOLDER'], app.config['ANALYSIS_RESULTS']]:
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            try:
                if os.path.isfile(filepath):
                    file_age = current_time - os.path.getmtime(filepath)
                    if file_age > max_age:
                        os.remove(filepath)
                        logger.info(f"Cleaned up old file: {filename}")
            except Exception as e:
                logger.warning(f"Error cleaning up file {filename}: {str(e)}")

if __name__ == '__main__':
    # Clean up old files on startup
    cleanup_old_files()
    
    # Start Flask app
    logger.info("Starting Word Intelligence Analytics Backend...")
    logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    logger.info(f"Spark master: {app.config['SPARK_MASTER']}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)