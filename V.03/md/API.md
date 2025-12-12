# API Documentation

## Base URL
```
http://localhost:8000/api
```

## Health Check
### GET `/health`
Check API health status
```bash
curl http://localhost:8000/health
```

**Response (200)**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Dashboard Endpoints

### GET `/dashboard/summary`
Get dashboard statistics and recent analyses
```bash
curl http://localhost:8000/api/dashboard/summary
```

**Response (200)**
```json
{
  "total_analyses": 42,
  "total_files": 25,
  "total_urls": 17,
  "avg_execution_time": 2.34,
  "recent_analyses": [
    {
      "id": "analysis_12345",
      "input_type": "file",
      "input_metadata": {"filename": "document.txt", "size": 50000},
      "status": "completed",
      "execution_time": 1.23,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:02Z"
    }
  ],
  "spark_status": {
    "master": "local[*]",
    "app_name": "WordAnalytics",
    "running_jobs": 0
  }
}
```

---

## File Analysis Endpoints

### POST `/analyze/file`
Upload and analyze a file
```bash
curl -X POST -F "file=@document.txt" http://localhost:8000/api/analyze/file
```

**Request**
- Content-Type: multipart/form-data
- file: Binary file to analyze (txt, pdf, doc, etc.)

**Response (200)**
```json
{
  "id": "analysis_12345",
  "input_type": "file",
  "input_metadata": {
    "filename": "document.txt",
    "size": 50000,
    "upload_time": "2024-01-15T10:30:00Z"
  },
  "status": "processing",
  "raw_data": null,
  "processed_data": null,
  "visualization_data": null,
  "execution_time": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

## URL Analysis Endpoints

### POST `/analyze/url`
Analyze content from a URL
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "timeout": 30}' \
  http://localhost:8000/api/analyze/url
```

**Request Body**
```json
{
  "url": "https://example.com",
  "timeout": 30
}
```

**Response (200)**
```json
{
  "id": "analysis_12346",
  "input_type": "url",
  "input_metadata": {
    "url": "https://example.com",
    "title": "Example Domain",
    "status_code": 200
  },
  "status": "processing",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

## Visualization Endpoints

### GET `/visualization/{analysis_id}`
Retrieve visualization data for an analysis
```bash
curl http://localhost:8000/api/visualization/analysis_12345
```

**Response (200)**
```json
{
  "word_frequency": {
    "type": "bar",
    "title": "Top 20 Words by Frequency",
    "labels": ["the", "and", "to", "of", "a"],
    "datasets": [
      {
        "label": "Frequency",
        "data": [245, 189, 156, 134, 128],
        "backgroundColor": "#0C66E4"
      }
    ]
  },
  "word_length_histogram": {...},
  "sentiment_pie": {...},
  "top_bigrams": {...},
  "trigrams": {...},
  "statistics": {
    "type": "stats",
    "title": "Analysis Statistics",
    "data": {
      "total_words": 5234,
      "unique_words": 1456,
      "avg_word_length": 4.23,
      "sentiment_score": 6.5,
      "execution_time": 1.23
    }
  }
}
```

---

## Raw Data Endpoints

### GET `/raw/{analysis_id}`
Get raw extracted text with pagination
```bash
curl "http://localhost:8000/api/raw/analysis_12345?skip=0&limit=100"
```

**Query Parameters**
- skip: Number of items to skip (default: 0)
- limit: Number of items to return (default: 100)

**Response (200)**
```json
{
  "data": "Lorem ipsum dolor sit amet...",
  "word_count": 5234,
  "character_count": 28456,
  "total_lines": 234
}
```

### GET `/raw/download/{analysis_id}`
Download raw data as text file
```bash
curl -O http://localhost:8000/api/raw/download/analysis_12345
```

**Response (200)**
- Content-Type: text/plain
- Returns the raw extracted text file

---

## History Endpoints

### GET `/history/all`
Get all analyses with pagination
```bash
curl "http://localhost:8000/api/history/all?skip=0&limit=20"
```

**Query Parameters**
- skip: Number of items to skip (default: 0)
- limit: Number of items to return (default: 20)

**Response (200)**
```json
{
  "items": [
    {
      "id": "analysis_12345",
      "input_type": "file",
      "input_metadata": {"filename": "document.txt"},
      "status": "completed",
      "execution_time": 1.23,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 42,
  "skip": 0,
  "limit": 20
}
```

### POST `/history/filter`
Filter analyses by criteria
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "input_type": "file",
    "status": "completed",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "skip": 0,
    "limit": 50
  }' \
  http://localhost:8000/api/history/filter
```

**Request Body**
```json
{
  "input_type": "file",
  "status": "completed",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "skip": 0,
  "limit": 50
}
```

**Response (200)**
```json
{
  "items": [...],
  "total": 25,
  "skip": 0,
  "limit": 50
}
```

---

## PySpark Execution Endpoints

### POST `/spark/submit`
Submit a PySpark analysis job
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "analysis_id": "analysis_12345",
    "input_type": "file",
    "text": "Sample text to analyze..."
  }' \
  http://localhost:8000/api/spark/submit
```

**Response (200)**
```json
{
  "job_id": "job_12345",
  "analysis_id": "analysis_12345",
  "status": "running",
  "message": "Job submitted successfully"
}
```

### GET `/spark/status/{job_id}`
Get PySpark job status
```bash
curl http://localhost:8000/api/spark/status/job_12345
```

**Response (200)**
```json
{
  "job_id": "job_12345",
  "status": "completed",
  "progress": 100,
  "metrics": {
    "total_words": 5234,
    "unique_words": 1456,
    "avg_word_length": 4.23,
    "sentiment_score": 6.5,
    "top_words": [
      {"word": "the", "count": 245},
      {"word": "and", "count": 189}
    ]
  }
}
```

### GET `/spark/logs/{job_id}`
Get PySpark job execution logs
```bash
curl http://localhost:8000/api/spark/logs/job_12345
```

**Response (200)**
```json
{
  "job_id": "job_12345",
  "logs": "2024-01-15 10:30:00 - Job started\n2024-01-15 10:30:01 - Processing text...",
  "level": "INFO"
}
```

---

## Cluster Endpoints

### GET `/cluster/metrics`
Get cluster health metrics
```bash
curl http://localhost:8000/api/cluster/metrics
```

**Response (200)**
```json
{
  "status": "healthy",
  "total_executors": 4,
  "active_executors": 4,
  "total_memory_gb": 8,
  "used_memory_gb": 2.5,
  "cpu_cores": 8,
  "tasks_running": 1,
  "tasks_queued": 0
}
```

### GET `/cluster/nodes`
Get individual executor/node status
```bash
curl http://localhost:8000/api/cluster/nodes
```

**Response (200)**
```json
{
  "nodes": [
    {
      "executor_id": "0",
      "status": "running",
      "memory_gb": 4.0,
      "used_memory_gb": 1.2,
      "cores": 4,
      "tasks": 1
    }
  ],
  "total_nodes": 4
}
```

### GET `/cluster/resources`
Get total cluster resource allocation
```bash
curl http://localhost:8000/api/cluster/resources
```

**Response (200)**
```json
{
  "total_memory_gb": 8,
  "available_memory_gb": 5.5,
  "total_cores": 8,
  "available_cores": 7,
  "max_concurrent_tasks": 8
}
```

---

## Error Responses

All endpoints may return errors with the following format:

### 400 Bad Request
```json
{
  "detail": "Invalid input provided",
  "status_code": 400
}
```

### 404 Not Found
```json
{
  "detail": "Analysis not found",
  "status_code": 404
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "status_code": 500
}
```

---

## Pagination

Most list endpoints support pagination:
- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum items to return (default: 20)

Example:
```bash
curl "http://localhost:8000/api/history/all?skip=20&limit=20"
```

---

## Rate Limiting

Currently no rate limiting is implemented. Production deployment should add:
- 100 requests/minute per IP for public endpoints
- 1000 requests/minute for authenticated endpoints
- 10 concurrent file uploads

---

## Authentication (Future)

Plans for OAuth2/JWT:
- POST `/auth/login` - User login
- POST `/auth/refresh` - Refresh token
- POST `/auth/logout` - User logout
- All protected endpoints will require Bearer token in Authorization header
