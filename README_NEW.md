# Word Intelligence & PySpark Analytics Platform

An enterprise-grade SaaS dashboard for analyzing word frequencies in text documents with professional data visualization, PySpark execution monitoring, and comprehensive NLP insights. Built with Flask, Chart.js, and modern enterprise UI principles.

---

## 🎨 Features

### Modern Enterprise Dashboard
- **Clean Professional Layout**: Snowflake/Datadog-inspired design with soft shadows and rounded cards
- **Sidebar Navigation**: Intuitive navigation between Dashboard, Visualizations, PySpark Execution, and Raw Data views
- **Top Action Bar**: Quick access to Upload File and Analyze URL functions
- **Responsive Grid System**: Adapts to different screen sizes and resolutions

### Multi-Format File Support
- **Text Files**: TXT, DOCX, PDF
- **Data Files**: CSV (extracts and analyzes all text content)
- **Web Files**: HTML/HTM (strips tags and analyzes content)
- **URL Analysis**: Fetch and analyze content directly from web URLs

### Advanced Visualizations
#### Summary Cards
- Total Words analyzed
- Unique Words count
- Sentiment Score (positive/neutral/negative)
- Processing Time metrics

#### Word Analysis Charts
- **Word Frequency Bar Chart**: Top 15 most common words (after stopword filtering)
- **Bigram Analysis**: Most frequent two-word phrases
- **Trigram Analysis**: Most frequent three-word phrases
- **Emotion Breakdown**: Donut chart showing joy, anger, fear, sadness, and neutral content
- **TF-IDF Topic Clusters**: Scatter plot visualization of document topics

### PySpark Execution Panel
A dedicated technical view showing real-time Spark job metrics:
- Job Status (Idle/Running/Succeeded/Failed)
- Progress bar with live updates
- Jobs, Stages, and Tasks counters
- Executor Memory usage
- Shuffle Read/Write metrics
- Average Task Time
- Skew Detection indicator
- Pipeline DAG visualization (Read → Tokenize → Filter → Count → Top-K)

### Raw Data Table
- **Searchable Table**: Live search across all analyzed words
- **Sortable Columns**: Word, Frequency, Normalized %, Length
- **Pagination**: 50 rows per page for performance
- **Export Functionality**: Download complete analysis as CSV

### Analysis Features
- **Custom Stopwords**: Filter common words from analysis
- **Real-time Updates**: Modify stopwords without re-uploading
- **History Tracking**: Save and retrieve previous analyses
- **Sentiment Detection**: Basic positive/negative analysis

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Aakash02A/Word-Count-Analyzer.git
cd Word-Count-Analyzer

# Install dependencies
pip install -r requirements.txt
```

### Required Packages
```
Flask==2.3.3
pandas==2.0.3
pymupdf==1.23.7
python-docx==0.8.11
requests==2.31.0
PyPDF2==3.0.1
pyspark==3.4.1
```

### Running the Application

```bash
# Start the Flask server
python app.py

# Open browser to http://localhost:5000
```

---

## 📖 Usage Guide

### 1. Upload a File
1. Click **"Upload File"** button in the top action bar
2. Drag & drop your file or click to browse
3. Optionally add comma-separated stopwords
4. Click **"Analyze File"**

### 2. Analyze a URL
1. Click **"Analyze URL"** button in the top action bar
2. Enter the website URL
3. Optionally add stopwords
4. Click **"Analyze URL"**

### 3. View Visualizations
Navigate to the **Visualizations** tab to see:
- Summary cards with key metrics
- Word frequency bar chart
- Bigram and Trigram analyses
- Emotion breakdown
- TF-IDF topic clusters

### 4. Monitor PySpark Execution
Switch to the **PySpark Execution** tab to view:
- Real-time job progress
- Executor metrics
- Pipeline DAG
- Task distribution

### 5. Explore Raw Data
Visit the **Raw Data** tab to:
- Search specific words
- Sort by frequency or length
- Navigate paginated results
- Export to CSV

---

## 🔧 API Endpoints

### Analyze File Upload
```http
POST /analyze
Content-Type: multipart/form-data

Parameters:
- file: File to analyze (TXT, DOCX, PDF, CSV, HTML)
- stopwords: Comma-separated list of stopwords (optional)

Response:
{
  "top_words": ["word1", "word2", ...],
  "top_counts": [100, 95, ...],
  "all_words": [...],
  "all_counts": [...],
  "total_words": 1500,
  "unique_words": 450,
  "filename": "document.txt",
  "csv_download": "/download/document_analysis.csv"
}
```

### Analyze URL Content
```http
POST /analyze_url
Content-Type: application/x-www-form-urlencoded

Parameters:
- url: URL to fetch and analyze
- stopwords: Comma-separated list of stopwords (optional)

Response: Same as /analyze
```

### Update Analysis with New Stopwords
```http
POST /api/update_analysis
Content-Type: application/x-www-form-urlencoded

Parameters:
- filename: Previously uploaded filename
- stopwords: New stopwords list

Response: Updated analysis data
```

### View Analysis History
```http
GET /list_history

Response:
[
  {
    "id": 1,
    "filename": "document.txt",
    "stored_at": "2025-01-15T10:30:00",
    "total_words": 1500,
    "unique_words": 450,
    ...
  },
  ...
]
```

### Get History Detail
```http
GET /history_detail/<id>

Response: Full analysis data for specific history entry
```

### Download CSV
```http
GET /download/<filename>

Response: CSV file download
```

---

## 🎨 UI Design Principles

### Enterprise SaaS Aesthetic
- **Color Palette**: Professional blues (#0C66E4, #1D7AFC) with semantic colors for success, warning, and danger
- **Typography**: System fonts (-apple-system, Inter, Segoe UI) for readability
- **Shadows**: Layered soft shadows for depth (sm, md, lg, xl)
- **Spacing**: Consistent 8px grid system
- **Borders**: Subtle borders (#E2E8F0) with rounded corners (8px-16px)

### Interaction Design
- **Hover States**: Smooth transitions with subtle lift effects
- **Loading States**: Progress bars and status indicators
- **Modals**: Backdrop blur with centered content
- **Responsive**: Mobile-friendly with collapsible sidebar

### Data Visualization
- **Chart.js**: Professional charts with custom colors and rounded bars
- **Color Gradients**: Blue spectrum for frequency, semantic colors for emotions
- **Tooltips**: Dark themed with border highlights
- **Grid Lines**: Subtle (#F1F5F9) for better readability

---

## 📁 Project Structure

```
Word-Count-Analyzer/
├── app.py                  # Flask application with all routes
├── pyspark_analyzer.py     # PySpark integration module
├── requirements.txt        # Python dependencies
├── history.json           # Analysis history storage
├── templates/
│   └── index.html         # Enterprise dashboard UI
├── uploads/               # Uploaded files and CSV exports
│   ├── *.txt
│   ├── *_analysis.csv
│   └── ...
└── README.md             # This file
```

---

## 🔒 Security Notes

- This is a development server. Use a production WSGI server (Gunicorn, uWSGI) for deployment.
- File uploads are sanitized and restricted to allowed extensions.
- URL analysis uses request timeouts to prevent hanging.
- No authentication implemented - add authentication for production use.

---

## 🐛 Troubleshooting

### PySpark not available
If you see "PySpark not available", the app will fall back to standard Python implementation. Install PySpark for enhanced performance:
```bash
pip install pyspark==3.4.1
```

### File upload errors
- Ensure file extensions are: .txt, .docx, .pdf, .csv, .html, .htm
- Check file encoding (UTF-8 recommended)
- Large files may take longer to process

### URL analysis fails
- Verify the URL is accessible
- Check network connectivity
- Some websites may block automated requests

### Charts not rendering
- Ensure Chart.js CDN is accessible
- Check browser console for JavaScript errors
- Clear browser cache and reload

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👤 Author

**Aakash02A**
- GitHub: [@Aakash02A](https://github.com/Aakash02A)
- Repository: [Word-Count-Analyzer](https://github.com/Aakash02A/Word-Count-Analyzer)

---

## 🙏 Acknowledgments

- Flask for the web framework
- Chart.js for beautiful visualizations
- PySpark for distributed text processing
- Enterprise SaaS design inspired by Snowflake, Datadog, and Databricks

---

## 📊 Dashboard Overview

The application features:
- **Sidebar Navigation**: Dashboard, Visualizations, PySpark Execution, Raw Data, Upload File, URL Analyzer
- **Top Action Bar**: Primary upload button, secondary URL button, supported file type indicators
- **Summary Cards**: Total Words, Unique Words, Sentiment Score, Processing Time
- **Visualizations Tab**: Word frequency chart, bigram/trigram analysis, emotion breakdown, TF-IDF clusters
- **PySpark Tab**: Job status, progress bar, metrics grid, DAG visualization
- **Raw Data Tab**: Searchable table, pagination, export to CSV

---

**Happy Analyzing! 📊✨**
