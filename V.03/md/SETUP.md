# Setup & Installation Guide

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- 4GB RAM minimum
- 2GB disk space for database and uploads

## Installation Steps

### 1. Clone or Navigate to Project
```bash
cd C:\Z\GITHUB\Word-Count-Analyzer\V.03
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
The `.env` file contains default configuration. Modify as needed:
```bash
# Database (default SQLite)
DATABASE_URL=sqlite:///./analytics.db

# PySpark Configuration
SPARK_MASTER=local[*]
SPARK_DRIVER_MEMORY=4g
SPARK_EXECUTOR_MEMORY=2g

# API Settings
LOG_LEVEL=INFO
DEBUG=False
```

### 5. Create Uploads Directory
```bash
# Windows
mkdir uploads

# Mac/Linux
mkdir -p uploads
```

### 6. Initialize Database
```bash
python -c "from backend.db.database import init_db; init_db()"
```

This creates `analytics.db` with all tables.

---

## Running the Application

### Development Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Production Server (with Gunicorn)
```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Accessing the Application

- **Web Interface**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## Docker Setup (Optional)

### Build Image
```bash
docker build -t word-analyzer:1.0 .
```

### Run Container
```bash
docker run -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/analytics.db:/app/analytics.db \
  word-analyzer:1.0
```

### Docker Compose
```bash
docker-compose up -d
```

---

## File Structure

```
V.03/
├── main.py                          # FastAPI application entry point
├── pyspark_analyzer.py              # Legacy PySpark analyzer
├── requirements.txt                 # Python dependencies
├── .env                             # Environment configuration
├── analytics.db                     # SQLite database (auto-created)
│
├── backend/
│   ├── db/
│   │   └── database.py              # SQLAlchemy setup & initialization
│   │
│   ├── models/
│   │   ├── analysis.py              # Analysis ORM model
│   │   ├── user.py                  # User ORM model
│   │   └── spark_job.py             # PySpark job tracking model
│   │
│   ├── services/
│   │   ├── pyspark_service.py       # Distributed text analysis with Spark
│   │   ├── file_analyzer.py         # File upload processing
│   │   ├── url_analyzer.py          # URL crawling & analysis
│   │   └── visualization_service.py # Chart & visualization generation
│   │
│   ├── schemas/
│   │   └── __init__.py              # Pydantic request/response schemas
│   │
│   ├── routes/
│   │   └── (future route modules)   # API endpoint organization
│   │
│   └── utils/
│       └── (future utilities)       # Helper functions
│
├── templates/
│   └── index.html                   # Single-page application
│
├── static/
│   ├── styles.css                   # Application styling
│   └── app.js                       # Client-side JavaScript
│
├── uploads/                         # Uploaded files storage
│   └── *.txt, *.csv                 # Analysis input & output files
│
└── md/
    ├── API.md                       # API endpoint documentation
    ├── SETUP.md                     # This file
    ├── ARCHITECTURE.md              # System design overview
    ├── DATABASE.md                  # Database schema documentation
    └── DEPLOYMENT.md                # Production deployment guide
```

---

## Common Issues & Troubleshooting

### Issue: PySpark Installation Fails
**Solution**: Install Java Development Kit (JDK) first
```bash
# Windows: Download from oracle.com or use:
choco install openjdk

# Mac:
brew install openjdk@11

# Linux (Ubuntu):
sudo apt-get install openjdk-11-jdk
```

### Issue: Port 8000 Already in Use
**Solution**: Use different port
```bash
uvicorn main:app --port 8001
```

### Issue: Database Lock Error
**Solution**: Delete `analytics.db` and reinitialize
```bash
rm analytics.db
python -c "from backend.db.database import init_db; init_db()"
```

### Issue: Out of Memory During Analysis
**Solution**: Reduce Spark memory in `.env`
```
SPARK_DRIVER_MEMORY=2g
SPARK_EXECUTOR_MEMORY=1g
```

### Issue: CORS Errors in Browser
**Solution**: Modify CORS_ORIGINS in `.env` to match your frontend URL

---

## Testing the API

### Health Check
```bash
curl http://localhost:8000/health
```

### Upload and Analyze File
```bash
curl -X POST -F "file=@sample.txt" http://localhost:8000/api/analyze/file
```

### Analyze URL
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}' \
  http://localhost:8000/api/analyze/url
```

### Get Dashboard Summary
```bash
curl http://localhost:8000/api/dashboard/summary
```

### View Visualizations
```bash
# Replace analysis_12345 with actual analysis ID
curl http://localhost:8000/api/visualization/analysis_12345
```

---

## Performance Tuning

### For Large Files (100+ MB)
Increase Spark memory in `.env`:
```
SPARK_DRIVER_MEMORY=8g
SPARK_EXECUTOR_MEMORY=4g
```

### For Slow Network
Increase timeouts in `.env`:
```
URL_TIMEOUT=60
```

### For High Concurrency
Add more workers:
```bash
gunicorn main:app --workers 8 --worker-class uvicorn.workers.UvicornWorker
```

---

## Database Management

### View Database Contents
```bash
# Install sqlite3 CLI tool if needed
sqlite3 analytics.db

# Common queries
sqlite> SELECT * FROM analysis;
sqlite> SELECT COUNT(*) FROM analysis;
sqlite> SELECT * FROM spark_job;
sqlite> .schema analysis  # View table structure
```

### Backup Database
```bash
cp analytics.db analytics.db.backup
```

### Reset Database
```bash
rm analytics.db
python -c "from backend.db.database import init_db; init_db()"
```

---

## Logging

Logs are printed to console by default. To save to file:

### Add to main.py
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

---

## Next Steps

1. Review [API.md](API.md) for complete API endpoint documentation
2. Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design details
3. Read [DATABASE.md](DATABASE.md) for database schema information
4. See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment guides

---

## Support & Documentation

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **PySpark Docs**: https://spark.apache.org/docs/latest/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Uvicorn Docs**: https://www.uvicorn.org/
