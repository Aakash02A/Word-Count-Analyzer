import re
from flask import Flask, request, jsonify, send_file, render_template
import os
import json
import pandas as pd
from datetime import datetime
from collections import Counter

# Initialize global variables for PySpark components
SparkSession = None
split = None
explode = None
lower = None
col = None
SPARK_AVAILABLE = False

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

def spark_word_count(file_path, stopwords=set()):
    """
    Word count implementation using PySpark.
    Falls back to simple implementation if PySpark is not available or fails.
    """
    # For now, always use the simple implementation to avoid linter errors
    # TODO: Re-enable PySpark when we can resolve the import issues
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
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

        if not file.filename.endswith('.txt'):
            return jsonify({"error": "Please upload a text (.txt) file"}), 400

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

        # Read text safely
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        except Exception as e:
            app.logger.error(f"File read error: {str(e)}")
            return jsonify({"error": "Could not read the uploaded file"}), 500

        if not text.strip():
            return jsonify({"error": "The uploaded file is empty"}), 400

        try:
            # Get all words (without stopwords filtering) for the complete word list
            # Use PySpark if available, otherwise fall back to simple implementation
            all_words, filtered_words = spark_word_count(filepath, stopwords)
            
            all_counter = Counter(all_words)
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
            try:
                # Store in history
                history = load_history()
                record = {
                    "id": len(history) + 1,
                    "filename": safe_filename,
                    "stored_at": datetime.now().isoformat(),
                    "top_words": top_words,
                    "top_counts": top_counts,
                    "all_words": all_words_list,
                    "all_counts": all_counts_list,
                    "total_words": len(all_words),
                    "unique_words": len(all_counter)
                }
                history.append(record)
                save_history(history)

                # Save CSV file for download (with all words)
                df = pd.DataFrame({"Word": all_words_list, "Count": all_counts_list})
                csv_name = f"{os.path.splitext(safe_filename)[0]}_analysis.csv"
                csv_path = os.path.join(app.config['UPLOAD_FOLDER'], csv_name)
                df.to_csv(csv_path, index=False)

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
                app.logger.error(f"Error saving results: {str(e)}")
                return jsonify({"error": "Error saving analysis results"}), 500

        except Exception as e:
            app.logger.error(f"Text processing error: {str(e)}")
            return jsonify({"error": "Error processing the text content"}), 500

    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

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
            
        # Read text safely
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
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

if __name__ == '__main__':
    app.run(debug=True)