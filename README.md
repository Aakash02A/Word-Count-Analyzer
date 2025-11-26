# Word Count Analyzer

A Flask-based web application for analyzing word frequencies in text documents, with support for multiple file formats and both basic Python and PySpark processing engines.

## Features

- **Multiple File Format Support**: Process TXT, DOCX, and PDF files
- **Flexible Text Analysis**: Count word frequencies with customizable stopwords
- **Dual Processing Engines**: Uses PySpark for large-scale analysis with fallback to Python for smaller files
- **Web Interface**: User-friendly dashboard for file upload and analysis
- **REST API**: Programmatic access to analysis functionality
- **URL Content Analysis**: Analyze text content directly from web URLs
- **History Tracking**: Save and retrieve previous analysis sessions
- **Data Export**: Download analysis results as CSV files
- **Real-time Updates**: Modify stopwords and re-analyze without re-uploading files

---

## Usage
### Required Pacakges Download

```
pip install -r requirements.txt
```

### Start the application

```
python pyspark_analyzer.py
python app.py
```
Open your browser and navigate to http://localhost:5000

### Use the web interface to

- Upload text files (TXT, DOCX, PDF)
- Enter stopwords (comma-separated)
- View word frequency charts
- Download analysis results
- Browse analysis history

---

## API Endpoints
### Analyze File Upload

```
POST /analyze
Content-Type: multipart/form-data

Parameters:
- file: File to analyze
- stopwords: Comma-separated list of stopwords
```

### Analyze URL Content
```
POST /analyze_url
Content-Type: application/x-www-form-urlencoded

Parameters:
- url: URL to fetch and analyze
- stopwords: Comma-separated list of stopwords
```

### Update Analysis
```
POST /api/update_analysis
Content-Type: application/x-www-form-urlencoded

Parameters:
- filename: Previously uploaded filename
- stopwords: New stopwords list
```

---

## History System

The application maintains a persistent history of all analyses in `history.json`.

### History File Location
- **Path**: `./history.json` (in application root directory)
- **Format**: JSON array of analysis records
- **Auto-generated**: Created automatically on first analysis

### History Record Structure

Each analysis is stored as a JSON object:

```json
{
  "id": 1,
  "filename": "document.txt",
  "stored_at": "2024-01-15T10:30:00.000000",
  "top_words": ["hello", "world", "test"],
  "top_counts": [15, 12, 8],
  "all_words": ["hello", "world", "test", "example"],
  "all_counts": [15, 12, 8, 5],
  "total_words": 150,
  "unique_words": 40
}

```

### Fields Description

- **id**: Unique sequential identifier
- **filename**: Original uploaded filename
- **stored_at**: ISO timestamp of analysis
- **top_words**: Top 15 most frequent words (after stopwords)
- **top_counts**: Corresponding counts for top words
- **all_words**: All unique words found in text
- **all_counts**: Frequency counts for all words
- **total_words**: Total word count in document
- **unique_words**: Number of unique words

---

## Supported File Formats

- **TXT**: Plain text files
- **DOCX**: Microsoft Word documents
- **PDF**: Portable Document Format files

## Features

- Word frequency analysis
- Custom stopwords filtering
- Multiple file format support
- URL content analysis
- CSV export
- Analysis history
- PySpark support for large files

---