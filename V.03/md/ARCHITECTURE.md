# Architecture Overview

## System Design

The Word Intelligence & PySpark Analytics Platform follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (SPA)                        │
│         HTML/CSS/JS (Single Page Application)           │
│  - Dashboard, Visualizations, PySpark UI, History, etc. │
└───────────┬───────────────────────────────────┬─────────┘
            │                                   │
        HTTP/REST                          WebSocket
            │                             (Future)
┌───────────▼───────────────────────────────────▼─────────┐
│                FastAPI Web Framework                    │
│  - Route handlers, Request/Response validation           │
│  - CORS, static file serving, health checks             │
└───────────┬───────────────────────────────────┬─────────┘
            │                                   │
        Endpoints                          Middleware
            │                                   │
┌───────────▼───────────────────────────────────▼─────────┐
│              Service Layer                              │
│  - PySparkService (text analysis)                       │
│  - FileAnalyzerService (file processing)                │
│  - URLAnalyzerService (web scraping)                    │
│  - VisualizationService (chart generation)              │
└───────────┬───────────────────────────────────┬─────────┘
            │                                   │
        Business Logic                    Data Processing
            │                                   │
┌───────────▼───────────────────────────────────▼─────────┐
│              Data Layer (SQLAlchemy ORM)                │
│  - Analysis model (persists analyses)                   │
│  - User model (user accounts)                           │
│  - SparkJob model (job tracking)                        │
└───────────┬───────────────────────────────────┬─────────┘
            │                                   │
         ORM                              Session Management
            │                                   │
┌───────────▼───────────────────────────────────▼─────────┐
│           Database (SQLite/PostgreSQL)                  │
│  - Tables: analysis, user, spark_job, etc.              │
└─────────────────────────────────────────────────────────┘
```

---

## Component Description

### 1. Frontend Layer

**Location**: `templates/index.html`, `static/`

**Components**:
- **Dashboard**: Summary statistics, recent analyses
- **File Upload**: Document upload interface
- **URL Analyzer**: Web page analysis input
- **Visualizations**: Charts, graphs, statistics
- **Raw Data**: Extracted text viewer with download
- **History**: Analysis history with filtering
- **PySpark UI**: Job submission and monitoring
- **Cluster Metrics**: Resource utilization dashboard

**Technology**:
- Pure HTML5 (no frameworks)
- Vanilla JavaScript (ES6+)
- CSS3 (modern styling, responsive)
- Fetch API for HTTP requests

**Key Features**:
- Client-side routing (no page reloads)
- Real-time status updates
- Responsive design (mobile, tablet, desktop)
- Data export capabilities

---

### 2. API Layer (FastAPI)

**Location**: `main.py`

**Responsibilities**:
- HTTP request handling
- Request validation (Pydantic schemas)
- Response serialization
- CORS configuration
- Static file serving
- Error handling and HTTP status codes

**Endpoints** (20+):
```
Health & Info:
  GET /health

Dashboard:
  GET /api/dashboard/summary

File Analysis:
  POST /api/analyze/file

URL Analysis:
  POST /api/analyze/url

Visualizations:
  GET /api/visualization/{analysis_id}

Raw Data:
  GET /api/raw/{analysis_id}
  GET /api/raw/download/{analysis_id}

History:
  GET /api/history/all
  POST /api/history/filter

PySpark Execution:
  POST /api/spark/submit
  GET /api/spark/status/{job_id}
  GET /api/spark/logs/{job_id}

Cluster Management:
  GET /api/cluster/metrics
  GET /api/cluster/nodes
  GET /api/cluster/resources
```

**Middleware**:
- CORS (Cross-Origin Resource Sharing)
- Error handling
- Request logging
- Response compression

---

### 3. Service Layer

**Location**: `backend/services/`

#### 3.1 PySparkService
**File**: `pyspark_service.py`

**Purpose**: Distributed text analysis using Apache Spark

**Key Methods**:
```python
analyze_text(text: str) -> dict
  - Input: Raw text
  - Processing: RDD operations, DataFrame grouping, aggregation
  - Output: Metrics (total_words, unique_words, top_words, sentiment, etc.)
  - Execution: Local Spark cluster (configurable)

submit_job(analysis_id: str, text: str) -> str
  - Submits async analysis job
  - Returns job_id for tracking

get_job_status(job_id: str) -> dict
  - Current job status: pending, running, completed, failed
  - Progress percentage

get_job_metrics(job_id: str) -> dict
  - Metrics: words, frequencies, sentiment
  - Statistics: avg length, distribution

get_logs(job_id: str) -> str
  - Job execution logs

stop()
  - Graceful Spark shutdown
```

**Configuration**:
- Master: `local[*]` (all available cores)
- Driver Memory: 4GB (configurable)
- Executor Memory: 2GB (configurable)
- App Name: WordAnalytics

**Analysis Pipeline**:
```
Raw Text
    ↓
Split into lines → Create RDD
    ↓
Split into words → Lowercase → Remove punctuation
    ↓
Create DataFrame
    ↓
Group by word → Count occurrences → Sort by frequency
    ↓
Calculate statistics:
  - Total words
  - Unique words
  - Average word length
  - Word length distribution
  - Top 50 words
  - Sentiment score
    ↓
Return results (execution_time tracked)
```

#### 3.2 FileAnalyzerService
**File**: `file_analyzer.py`

**Purpose**: Orchestrate file upload analysis

**Key Methods**:
```python
analyze(file_path: str) -> dict
  1. Read file (UTF-8, handle encoding errors)
  2. Extract raw text
  3. Call PySparkService.analyze_text()
  4. Call VisualizationService.generate_visualizations()
  5. Return: raw_data, processed_data, visualization_data, execution_time
```

**Supported Formats**:
- .txt (plain text)
- .pdf (with text extraction)
- .doc/.docx (with text extraction)
- .csv (with parsing)

#### 3.3 URLAnalyzerService
**File**: `url_analyzer.py`

**Purpose**: Fetch and analyze web page content

**Key Methods**:
```python
analyze(url: str, timeout: int = 30) -> dict
  1. Async HTTP GET request (aiohttp)
  2. Parse HTML with HTMLParser
  3. Extract text content
  4. Call PySparkService.analyze_text()
  5. Call VisualizationService.generate_visualizations()
  6. Return: raw_data, processed_data, visualization_data, execution_time, metadata
```

**Features**:
- Async/await (non-blocking I/O)
- HTML stripping (removes tags)
- Metadata extraction (title, status code)
- Error handling (connection, timeout)
- 30-second timeout default

#### 3.4 VisualizationService
**File**: `visualization_service.py`

**Purpose**: Generate chart data for frontend visualization

**Key Methods**:
```python
generate_visualizations(analysis_result: dict) -> dict
  Generates 6 chart types:
  1. Word Frequency Bar Chart (top 20 words)
  2. Word Length Distribution Histogram
  3. Sentiment Distribution Pie Chart
  4. Top Bigrams Table
  5. Top Trigrams Table
  6. Statistics Summary
```

**Output Format** (Chart.js compatible):
```json
{
  "word_frequency": {
    "type": "bar",
    "labels": ["the", "and", "to"],
    "datasets": [{"label": "Frequency", "data": [245, 189, 156]}]
  },
  ...
}
```

---

### 4. Data Layer (SQLAlchemy ORM)

**Location**: `backend/models/`, `backend/db/`

#### 4.1 Database Configuration
**File**: `backend/db/database.py`

```python
Engine: SQLite (configurable to PostgreSQL)
URL: sqlite:///./analytics.db

SessionLocal: Thread-safe session factory
Base: Declarative base for ORM models

init_db(): Create all tables on startup
```

#### 4.2 ORM Models

**Analysis Model** (`backend/models/analysis.py`)
```python
Table: analysis
Columns:
  - id: String (UUID) PRIMARY KEY
  - input_type: String (file, url)
  - input_metadata: JSON (filename/url, size, etc.)
  - status: String (processing, completed, failed)
  - raw_data: Text (extracted content)
  - processed_data: JSON (analysis results)
  - visualization_data: JSON (chart data)
  - execution_time: Float (seconds)
  - created_at: DateTime (auto)
  - updated_at: DateTime (auto-update)

Relationships:
  - One-to-many with SparkJob
```

**User Model** (`backend/models/user.py`)
```python
Table: user
Columns:
  - id: String (UUID) PRIMARY KEY
  - username: String UNIQUE
  - email: String UNIQUE
  - hashed_password: String
  - is_active: Boolean
  - total_analyses: Integer
  - last_login: DateTime
  - created_at: DateTime

Relationships:
  - (Future) One-to-many with Analysis
```

**SparkJob Model** (`backend/models/spark_job.py`)
```python
Table: spark_job
Columns:
  - id: String (UUID) PRIMARY KEY
  - analysis_id: String FK → analysis.id
  - job_id: String (Spark job ID)
  - status: String (pending, running, completed, failed)
  - metrics: JSON (execution metrics)
  - logs: Text (job logs)
  - created_at: DateTime
  - completed_at: DateTime (nullable)
```

---

## Data Flow Diagram

### File Upload Analysis Flow
```
User uploads file
      ↓
POST /api/analyze/file
      ↓
FastAPI handler
  - Validate file size
  - Save to uploads/
  - Create Analysis record (status=processing)
      ↓
FileAnalyzerService.analyze()
  - Read file content
      ↓
PySparkService.analyze_text()
  - Distribute to Spark cluster
  - Process in parallel
  - Return metrics
      ↓
VisualizationService.generate_visualizations()
  - Generate 6 chart types
  - Format as JSON
      ↓
Update Analysis record
  - Set raw_data, processed_data, visualization_data
  - Set status=completed, execution_time
      ↓
Return Analysis to client
      ↓
Frontend updates UI with visualizations
```

### URL Analysis Flow
```
User submits URL
      ↓
POST /api/analyze/url
      ↓
URLAnalyzerService.analyze()
  - Async HTTP GET (aiohttp)
  - Parse HTML
  - Extract text
      ↓
PySparkService.analyze_text()
  - Same as file analysis
      ↓
VisualizationService.generate_visualizations()
      ↓
Save Analysis + visualizations to database
      ↓
Return to client
```

### Real-time Job Tracking Flow
```
POST /api/spark/submit
      ↓
PySparkService.submit_job()
  - Start async Spark job
  - Store job_id in tracking dict
  - Return job_id
      ↓
Client polls GET /api/spark/status/{job_id}
      ↓
Service returns status + progress
      ↓
When completed, client calls:
  GET /api/visualization/{analysis_id}
      ↓
Frontend displays results
```

---

## Key Design Patterns

### 1. Dependency Injection
```python
# In FastAPI routes
def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usage in endpoint
@app.post("/api/analyze/file")
async def analyze_file(file: UploadFile, db: Session = Depends(get_db)):
    ...
```

### 2. Service Layer Pattern
```python
# Separation of concerns
# APILayer (main.py) ← ServiceLayer ← DataLayer

class FileAnalyzerService:
    def analyze(self, file_path) → dict
        # Orchestrate analysis workflow

class PySparkService:
    def analyze_text(self, text) → dict
        # Distributed computation

class VisualizationService:
    def generate_visualizations(self, results) → dict
        # Chart generation
```

### 3. Async/Await Pattern
```python
# Non-blocking I/O for URL analysis
async def analyze(self, url: str) → dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
```

### 4. ORM Pattern
```python
# Type-safe database operations
analysis = Analysis(
    input_type="file",
    input_metadata={...},
    status="processing"
)
db.add(analysis)
db.commit()

# Query
result = db.query(Analysis).filter(Analysis.id == "123").first()
```

---

## Technology Stack

| Layer | Component | Technology | Purpose |
|-------|-----------|-----------|---------|
| Frontend | UI/UX | HTML5, CSS3, Vanilla JS | User interface |
| API | Web Framework | FastAPI | HTTP endpoint handling |
| API | Server | Uvicorn | ASGI server |
| Business Logic | Distributed Processing | Apache Spark | Parallel text analysis |
| Business Logic | Services | Python, aiohttp | Service orchestration |
| Data | ORM | SQLAlchemy | Database abstraction |
| Data | Database | SQLite (dev), PostgreSQL (prod) | Data persistence |
| Validation | Schema | Pydantic | Request/response validation |

---

## Scalability Considerations

### Horizontal Scaling
- **Frontend**: Serve from CDN
- **API**: Load balance multiple Uvicorn/Gunicorn instances
- **Database**: PostgreSQL with replication (replace SQLite)
- **Spark**: Deploy Spark cluster with multiple executors

### Vertical Scaling
- **Spark Memory**: Increase SPARK_DRIVER_MEMORY, SPARK_EXECUTOR_MEMORY
- **Database**: Add indexes for common queries
- **API Workers**: Increase Uvicorn/Gunicorn workers

### Caching
- Cache analysis results (Redis)
- Cache visualization data
- Client-side caching (HTTP headers)

---

## Security Considerations

### Current Implementation
- CORS enabled for all origins (change for production)
- No authentication (future: OAuth2, JWT)
- No rate limiting (future: middleware)
- Input validation via Pydantic schemas

### Production Recommendations
1. Implement JWT authentication
2. Add API rate limiting
3. Use HTTPS (SSL/TLS)
4. Sanitize file uploads
5. Validate URLs (prevent SSRF)
6. Add request logging/audit
7. Use environment variables for secrets
8. Implement CSRF protection

---

## Performance Characteristics

### Analysis Time
- Small files (<1MB): 0.5-2 seconds
- Medium files (1-100MB): 2-30 seconds
- Large files (100MB+): 30-300 seconds
- Depends on Spark cluster configuration

### Database Queries
- Dashboard summary: ~100ms (count aggregations)
- History retrieval: ~50-200ms (pagination)
- Visualization retrieval: ~10-50ms (simple join)

### Optimization Opportunities
- Database query optimization with indexes
- Result caching with Redis
- Async processing with task queue (Celery)
- Spark caching for repeated analyses
- Frontend lazy loading

---

## Future Enhancements

1. **User Authentication**: OAuth2, multi-user support
2. **Real-time Updates**: WebSocket support
3. **Advanced NLP**: Sentiment analysis, entity extraction
4. **Custom Dictionaries**: User-defined word lists
5. **Scheduling**: Batch analysis jobs
6. **Export Formats**: PDF reports, Excel exports
7. **API Keys**: Third-party API access
8. **Analytics**: Usage tracking, insights
9. **Notifications**: Email alerts, webhooks
10. **Clustering**: Distributed Spark deployment

---

## Related Documentation

- [API.md](API.md) - Endpoint specification
- [DATABASE.md](DATABASE.md) - Database schema
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
- [SETUP.md](SETUP.md) - Installation & configuration
