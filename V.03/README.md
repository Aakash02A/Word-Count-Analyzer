# Word Intelligence & PySpark Analytics Platform

A production-ready text analysis platform featuring distributed PySpark processing, real-time visualizations, and comprehensive analytics on document content.

## 🎯 Key Features

✅ **File Upload Analysis** - Upload documents for instant text analysis
✅ **URL Analysis** - Fetch and analyze web page content
✅ **Distributed Processing** - PySpark-powered parallel text analysis
✅ **Real-time Visualizations** - Interactive charts and statistics
✅ **History & Filtering** - Track analyses with advanced search
✅ **Cluster Monitoring** - View Spark cluster health and metrics
✅ **Raw Data Export** - Download extracted content as text files
✅ **REST API** - 20+ endpoints for programmatic access
✅ **Production Ready** - Docker, Kubernetes, and monitoring support

## 🏗️ Architecture

```
Frontend (HTML/CSS/JS)
        ↓
FastAPI REST API (20+ endpoints)
        ↓
Service Layer (PySpark, URL Analysis, Visualization)
        ↓
SQLAlchemy ORM (Analysis, User, SparkJob models)
        ↓
SQLite/PostgreSQL Database
```

## 📦 Tech Stack

- **Backend**: FastAPI, Uvicorn, SQLAlchemy
- **Processing**: Apache Spark (RDD/DataFrame)
- **Database**: SQLite (dev), PostgreSQL (production)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Async**: aiohttp (URL crawling)
- **Validation**: Pydantic schemas
- **Containerization**: Docker, Docker Compose
- **Orchestration**: Kubernetes ready

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python -c "from backend.db.database import init_db; init_db()"
```

### 3. Run Development Server

```bash
uvicorn main:app --reload --port 8000
```

### 4. Access Application

- **Web Interface**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

### Manual Docker Build

```bash
# Build image
docker build -t word-analyzer:1.0 .

# Run container
docker run -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -e DATABASE_URL=sqlite:///./analytics.db \
  word-analyzer:1.0
```

## 📊 Project Structure

```
V.03/
├── main.py                          # FastAPI application
├── requirements.txt                 # Python dependencies
├── .env                             # Environment configuration
├── Dockerfile                       # Docker image definition
├── docker-compose.yml               # Multi-container setup
├── nginx.conf                       # Nginx reverse proxy config
│
├── backend/
│   ├── db/
│   │   └── database.py              # SQLAlchemy setup
│   ├── models/
│   │   ├── analysis.py              # Analysis ORM model
│   │   ├── user.py                  # User ORM model
│   │   └── spark_job.py             # PySpark job tracking
│   ├── services/
│   │   ├── pyspark_service.py       # Distributed text analysis
│   │   ├── file_analyzer.py         # File processing
│   │   ├── url_analyzer.py          # Web scraping
│   │   └── visualization_service.py # Chart generation
│   ├── schemas/
│   │   └── __init__.py              # Pydantic request/response schemas
│   └── routes/
│       └── (route modules - future)
│
├── templates/
│   └── index.html                   # SPA interface
├── static/
│   ├── styles.css                   # Styling
│   └── app.js                       # Client-side logic
├── uploads/                         # Uploaded files storage
│
└── md/
    ├── API.md                       # API documentation
    ├── SETUP.md                     # Installation guide
    ├── ARCHITECTURE.md              # System design
    ├── DATABASE.md                  # Database schema
    └── DEPLOYMENT.md                # Production deployment
```

## 🔌 API Endpoints

### Dashboard
- `GET /api/dashboard/summary` - Get dashboard statistics

### Analysis
- `POST /api/analyze/file` - Upload and analyze file
- `POST /api/analyze/url` - Analyze URL content

### Visualizations
- `GET /api/visualization/{analysis_id}` - Get visualization data

### Raw Data
- `GET /api/raw/{analysis_id}` - Get extracted text
- `GET /api/raw/download/{analysis_id}` - Download as file

### History
- `GET /api/history/all` - Get analysis history
- `POST /api/history/filter` - Filter by criteria

### PySpark
- `POST /api/spark/submit` - Submit analysis job
- `GET /api/spark/status/{job_id}` - Get job status
- `GET /api/spark/logs/{job_id}` - Get job logs

### Cluster
- `GET /api/cluster/metrics` - Cluster health
- `GET /api/cluster/nodes` - Node status
- `GET /api/cluster/resources` - Resource allocation

See [API.md](md/API.md) for detailed endpoint documentation.

## 📚 Documentation

- **[SETUP.md](md/SETUP.md)** - Installation & configuration
- **[API.md](md/API.md)** - Complete API reference
- **[ARCHITECTURE.md](md/ARCHITECTURE.md)** - System design & data flow
- **[DATABASE.md](md/DATABASE.md)** - Database schema & queries
- **[DEPLOYMENT.md](md/DEPLOYMENT.md)** - Production deployment guide

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Database
DATABASE_URL=sqlite:///./analytics.db

# Logging
LOG_LEVEL=INFO

# PySpark
SPARK_MASTER=local[*]
SPARK_DRIVER_MEMORY=4g
SPARK_EXECUTOR_MEMORY=2g

# File Upload
MAX_UPLOAD_SIZE=52428800  # 50MB
UPLOAD_DIR=./uploads

# CORS
CORS_ORIGINS=["http://localhost:8000"]
```

## 🔍 Analysis Features

### Text Metrics
- **Total Words**: Count of all words in text
- **Unique Words**: Distinct word count
- **Average Length**: Mean word length
- **Word Distribution**: Frequency of each length category

### Top Words
- **Top 50 Words**: Most frequent words with counts
- **Bigrams**: Top 2-word phrases
- **Trigrams**: Top 3-word phrases

### Sentiment Analysis
- **Sentiment Score**: 0-10 scale (0=very negative, 10=very positive)
- **Distribution**: Positive/Negative/Neutral percentages

### Visualizations
- **Word Frequency Bar Chart**: Top 20 words
- **Word Length Histogram**: Distribution by length
- **Sentiment Pie Chart**: Emotional distribution
- **Statistics Summary**: Key metrics

## 🔐 Security

### Implemented
- ✅ CORS configuration
- ✅ Input validation (Pydantic)
- ✅ Error handling
- ✅ Logging

### Recommended for Production
- 🔒 HTTPS/SSL (nginx)
- 🔑 JWT authentication
- 🚦 Rate limiting
- 📊 Request logging
- 🛡️ Web Application Firewall
- 🔍 SQL injection prevention
- 🌐 SSRF protection

See [DEPLOYMENT.md](md/DEPLOYMENT.md) for security hardening.

## 📈 Performance

### Typical Analysis Times
- Small files (<1MB): 0.5-2 seconds
- Medium files (1-100MB): 2-30 seconds
- Large files (100MB+): 30-300 seconds

### Database Queries
- Dashboard summary: ~100ms
- History retrieval: ~50-200ms
- Visualization lookup: ~10-50ms

### Scalability
- **Horizontal**: Load balance multiple API instances
- **Vertical**: Increase Spark memory, database resources
- **Caching**: Redis for visualization data
- **Async**: Task queue for long-running jobs (Celery)

## 🧪 Testing

### Health Check

```bash
curl http://localhost:8000/health
```

### Upload File

```bash
curl -X POST -F "file=@sample.txt" http://localhost:8000/api/analyze/file
```

### Analyze URL

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}' \
  http://localhost:8000/api/analyze/url
```

### View Visualizations

```bash
# Get an analysis ID first, then:
curl http://localhost:8000/api/visualization/{analysis_id}
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
lsof -i :8000  # Find process
kill -9 <PID>  # Kill process
# Or use different port:
uvicorn main:app --port 8001
```

### PySpark Installation Issues
Install Java Development Kit:
```bash
# Ubuntu
sudo apt-get install openjdk-11-jdk

# Mac
brew install openjdk@11

# Windows
choco install openjdk
```

### Database Errors
```bash
# Reset database
rm analytics.db
python -c "from backend.db.database import init_db; init_db()"
```

See [SETUP.md](md/SETUP.md) for more troubleshooting.

## 📦 Dependencies

### Core
- fastapi==0.104.1
- uvicorn==0.24.0
- sqlalchemy==2.0.23
- pydantic==2.5.0
- pyspark==3.5.0

### Utilities
- aiohttp==3.9.1
- python-multipart==0.0.6
- python-dotenv==1.0.0

See [requirements.txt](requirements.txt) for full list.

## 🚢 Deployment

### Development
```bash
uvicorn main:app --reload
```

### Production (Gunicorn)
```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker
```bash
docker-compose up -d
```

### Kubernetes
```bash
kubectl apply -f deployment.yaml
```

See [DEPLOYMENT.md](md/DEPLOYMENT.md) for detailed production setup.

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👥 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Open pull request

## 📞 Support

For issues, questions, or suggestions:
- Check [SETUP.md](md/SETUP.md) for installation help
- Review [API.md](md/API.md) for endpoint details
- See [DEPLOYMENT.md](md/DEPLOYMENT.md) for production guidance
- Check existing GitHub issues

## 🎓 Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com
- **PySpark**: https://spark.apache.org/docs/latest/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Docker**: https://docs.docker.com/
- **Kubernetes**: https://kubernetes.io/docs/

## 🔮 Future Enhancements

- [ ] User authentication (OAuth2/JWT)
- [ ] Real-time WebSocket updates
- [ ] Advanced NLP (entity extraction, named recognition)
- [ ] Custom word lists and dictionaries
- [ ] Batch job scheduling
- [ ] PDF/Excel export formats
- [ ] Usage analytics and insights
- [ ] Multi-language support
- [ ] Distributed Spark deployment
- [ ] Webhook notifications

## 📊 Status

- ✅ Core backend: Complete
- ✅ REST API: Complete (20+ endpoints)
- ✅ Database models: Complete
- ✅ Service layer: Complete
- ✅ Frontend UI: Complete
- ✅ Docker support: Complete
- ✅ Documentation: Complete
- 🚧 Authentication: Planned
- 🚧 WebSocket: Planned

## Version

**Current Version**: 1.0.0

---

**Last Updated**: January 2024

Built with ❤️ using FastAPI, PySpark, and SQLAlchemy
