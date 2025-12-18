import sqlite3
import json
from datetime import datetime
import os

DB_NAME = 'analytics.db'

def init_db():
    """Initialize the database with necessary tables."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Analysis History Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,       -- 'file' or 'url'
            filename TEXT,              -- Name of file or URL
            content_hash TEXT,          -- To prevent duplicates if needed (optional)
            total_words INTEGER,
            unique_words INTEGER,
            top_words TEXT,             -- JSON string of words
            top_counts TEXT,            -- JSON string of counts
            bigrams TEXT,               -- JSON string
            sentiment_score REAL,
            sentiment_label TEXT,
            topics TEXT,                -- JSON string
            word_distribution TEXT,     -- JSON string (New)
            length_distribution TEXT,   -- JSON string (New)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check for new columns in existing table (Simple migration mainly for dev)
    try:
        c.execute("ALTER TABLE analysis_history ADD COLUMN word_distribution TEXT")
    except: pass
    try:
        c.execute("ALTER TABLE analysis_history ADD COLUMN length_distribution TEXT")
    except: pass
    
    conn.commit()
    conn.close()

def add_analysis_record(data):
    """
    Add a new analysis record to the database.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO analysis_history 
            (source, filename, total_words, unique_words, top_words, top_counts, bigrams, 
             sentiment_score, sentiment_label, topics, word_distribution, length_distribution, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('source', 'unknown'),
            data.get('filename', 'unknown'),
            data.get('total_words', 0),
            data.get('unique_words', 0),
            json.dumps(data.get('top_words', [])),
            json.dumps(data.get('top_counts', [])),
            json.dumps(data.get('bigrams', [])),
            data.get('sentiment_score', 0.0),
            data.get('sentiment_label', 'Neutral'),
            json.dumps(data.get('topics', [])),
            json.dumps(data.get('word_distribution', {})),
            json.dumps(data.get('length_distribution', {})),
            datetime.now().isoformat()
        ))
        
        record_id = c.lastrowid
        conn.commit()
        return record_id
    except Exception as e:
        print(f"Error adding record: {e}")
        return None
    finally:
        conn.close()

def get_all_history():
    """Retrieve all history records, newest first."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Access columns by name
    c = conn.cursor()
    
    c.execute('SELECT * FROM analysis_history ORDER BY id DESC')
    rows = c.fetchall()
    
    history = []
    for row in rows:
        history.append({
            'id': row['id'],
            'source': row['source'],
            'filename': row['filename'],
            'total_words': row['total_words'],
            'unique_words': row['unique_words'],
            'stored_at': row['created_at']
        })
        
    conn.close()
    return history

def get_record_by_id(record_id):
    """Retrieve full details for a specific record."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('SELECT * FROM analysis_history WHERE id = ?', (record_id,))
    row = c.fetchone()
    
    if row:
        record = dict(row)
        # Parse JSON fields back to objects
        try: record['top_words'] = json.loads(record['top_words'])
        except: record['top_words'] = []

        try: record['top_counts'] = json.loads(record['top_counts'])
        except: record['top_counts'] = []
            
        try: record['bigrams'] = json.loads(record['bigrams'])
        except: record['bigrams'] = []
            
        try: record['topics'] = json.loads(record['topics'])
        except: record['topics'] = []
        
        try: record['word_distribution'] = json.loads(record['word_distribution'])
        except: record['word_distribution'] = {}
        
        try: record['length_distribution'] = json.loads(record['length_distribution'])
        except: record['length_distribution'] = {}
        
        conn.close()
        return record
    
    conn.close()
    return None

def delete_record(record_id):
    """Delete a record by ID."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM analysis_history WHERE id = ?', (record_id,))
    conn.commit()
    conn.close()

def get_dashboard_stats():
    """Get aggregated statistics for the dashboard."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Total analyses
    c.execute('SELECT COUNT(*) FROM analysis_history')
    total_analyses = c.fetchone()[0]
    
    # Files processed
    c.execute("SELECT COUNT(*) FROM analysis_history WHERE source = 'file'")
    files_processed = c.fetchone()[0]
    
    # URLs analyzed
    c.execute("SELECT COUNT(*) FROM analysis_history WHERE source = 'url'")
    urls_analyzed = c.fetchone()[0]
    
    # Recent analyses (last 5)
    c.execute('SELECT source, created_at FROM analysis_history ORDER BY id DESC LIMIT 5')
    recent_rows = c.fetchall()
    
    recent_analyses = []
    for row in recent_rows:
        # Calculate time ago roughly
        try:
            dt = datetime.fromisoformat(row[1])
            time_str = dt.strftime("%Y-%m-%d %H:%M")
        except:
            time_str = "Just now"
            
        recent_analyses.append({
            'type': row[0],
            'status': 'Completed', # Assuming all saved are completed
            'time': time_str
        })
        
    conn.close()
    
    return {
        'total_analyses': total_analyses,
        'files_processed': files_processed,
        'urls_analyzed': urls_analyzed,
        'recent_analyses': recent_analyses,
        'avg_time': '0.5s' # Placeholder
    }

# Initialize on module load if file doesn't exist
if not os.path.exists(DB_NAME):
    init_db()
