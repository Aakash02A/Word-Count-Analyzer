# Production Deployment Guide

## Pre-Deployment Checklist

- [ ] Review security configuration
- [ ] Set up SSL/TLS certificates
- [ ] Configure production database (PostgreSQL)
- [ ] Set up environment variables
- [ ] Configure logging and monitoring
- [ ] Set up backup strategy
- [ ] Configure CORS for production domain
- [ ] Enable rate limiting
- [ ] Set up CI/CD pipeline
- [ ] Conduct security audit
- [ ] Load test the application

---

## Security Hardening

### 1. Environment Configuration

Create `.env.production`:
```bash
# Database
DATABASE_URL=postgresql://prod_user:secure_password@db.prod.example.com:5432/word_analyzer

# Security
DEBUG=False
SECRET_KEY=<random-secure-key-min-32-chars>
ALLOWED_HOSTS=api.example.com,www.example.com

# API
LOG_LEVEL=WARNING
WORKERS=8

# PySpark
SPARK_MASTER=spark://spark-master:7077
SPARK_DRIVER_MEMORY=8g
SPARK_EXECUTOR_MEMORY=4g

# CORS
CORS_ORIGINS=["https://example.com"]
CORS_ALLOW_CREDENTIALS=true

# File Upload
MAX_UPLOAD_SIZE=104857600  # 100MB
UPLOAD_DIR=/var/uploads

# Authentication (if enabled)
JWT_SECRET=<random-secure-key>
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600
```

### 2. Database Security

```python
# Use environment variables, never hardcode
import os
DATABASE_URL = os.getenv("DATABASE_URL")

# Enable SSL for PostgreSQL
# postgresql://user:password@host:5432/db?sslmode=require
```

### 3. CORS Configuration

```python
# main.py - Production CORS
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com", "https://www.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600
)
```

### 4. HTTPS/SSL Configuration

**Using Nginx as reverse proxy**:
```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.example.com;
    return 301 https://$server_name$request_uri;
}
```

### 5. Rate Limiting

Add to `main.py`:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/dashboard/summary")
@limiter.limit("60/minute")
async def dashboard_summary(request: Request, ...):
    ...
```

### 6. Input Validation & Sanitization

```python
# Already using Pydantic for validation
from pydantic import BaseModel, validator

class URLAnalysisRequest(BaseModel):
    url: str
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Invalid URL')
        # Prevent SSRF attacks
        if any(host in v for host in ['localhost', '127.0.0.1', '192.168']):
            raise ValueError('Private network access not allowed')
        return v
```

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Docker Compose for Production

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: word_analyzer
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/word_analyzer
      LOG_LEVEL: WARNING
      DEBUG: "False"
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./uploads:/app/uploads
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api

volumes:
  postgres_data:
```

### Build & Deploy

```bash
# Build image
docker build -t word-analyzer:1.0 .

# Run
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f api

# Scale workers
docker-compose up -d --scale api=3
```

---

## Kubernetes Deployment (K8s)

### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: word-analyzer-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: word-analyzer-api
  template:
    metadata:
      labels:
        app: word-analyzer-api
    spec:
      containers:
      - name: api
        image: word-analyzer:1.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: LOG_LEVEL
          value: "WARNING"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: word-analyzer-service
spec:
  selector:
    app: word-analyzer-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Deploy to K8s

```bash
# Create namespace
kubectl create namespace word-analyzer

# Create secrets
kubectl create secret generic db-secret \
  --from-literal=url=$DATABASE_URL \
  -n word-analyzer

# Deploy
kubectl apply -f deployment.yaml -n word-analyzer

# Check status
kubectl get pods -n word-analyzer

# View logs
kubectl logs -f deployment/word-analyzer-api -n word-analyzer

# Scale
kubectl scale deployment word-analyzer-api --replicas=5 -n word-analyzer
```

---

## Performance Optimization

### 1. Database Optimization

```python
# Add connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600,
    echo=False  # Disable SQL logging in production
)
```

### 2. Caching with Redis

```python
import redis
from functools import lru_cache

redis_client = redis.Redis(host='redis', port=6379, db=0)

@app.get("/api/visualization/{analysis_id}")
async def get_visualization(analysis_id: str):
    # Check cache first
    cached = redis_client.get(f"viz:{analysis_id}")
    if cached:
        return json.loads(cached)
    
    # Fetch from DB
    viz_data = {...}
    
    # Cache for 1 hour
    redis_client.setex(
        f"viz:{analysis_id}",
        3600,
        json.dumps(viz_data)
    )
    
    return viz_data
```

### 3. Async Processing

For long-running tasks:

```python
from celery import Celery

celery_app = Celery('word-analyzer')

@celery_app.task
def analyze_file_task(file_path: str):
    # Long-running analysis
    result = pyspark_service.analyze_text(...)
    return result

# In API
@app.post("/api/analyze/file")
async def analyze_file(file: UploadFile):
    # Queue task
    task = analyze_file_task.delay(file_path)
    return {"task_id": task.id}

# Check status
@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    task = analyze_file_task.AsyncResult(task_id)
    return {
        "id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }
```

### 4. CDN for Static Assets

```python
# Serve frontend from CDN
# Upload templates/ and static/ to CloudFront/Cloudflare
# Update main.py to serve from CDN

@app.get("/")
async def serve_index():
    # Redirect to CDN
    return RedirectResponse(url="https://cdn.example.com/index.html")
```

---

## Monitoring & Logging

### 1. Application Logging

```python
# Structured logging
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Usage
logger.info("Analysis completed", extra={
    "analysis_id": "123",
    "execution_time": 1.23,
    "status": "completed"
})
```

### 2. Metrics with Prometheus

```python
from prometheus_client import Counter, Histogram, start_http_server

# Metrics
analyses_total = Counter(
    'analyses_total',
    'Total analyses',
    ['input_type', 'status']
)
analysis_duration = Histogram(
    'analysis_duration_seconds',
    'Analysis duration',
    buckets=[0.1, 0.5, 1.0, 5.0, 10.0]
)

# In API
@app.post("/api/analyze/file")
async def analyze_file(file: UploadFile):
    with analysis_duration.time():
        # Analysis logic
        analyses_total.labels(
            input_type='file',
            status='completed'
        ).inc()
```

### 3. Monitoring Setup

**Prometheus config** (`prometheus.yml`):
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'word-analyzer'
    static_configs:
      - targets: ['localhost:8000/metrics']
```

**Grafana Dashboard**:
- Total analyses over time
- Average execution time
- API response times
- Database connection pool usage
- Memory/CPU utilization

---

## Backup & Disaster Recovery

### 1. Database Backups

```bash
# Daily PostgreSQL backup
0 2 * * * pg_dump -U ${DB_USER} word_analyzer > /backups/db_$(date +\%Y\%m\%d).sql

# Upload to S3
0 3 * * * aws s3 cp /backups/db_*.sql s3://backups-bucket/db/
```

### 2. File Uploads Backup

```bash
# Daily uploads backup
0 2 * * * tar -czf /backups/uploads_$(date +\%Y\%m\%d).tar.gz ./uploads

# Upload to S3
0 3 * * * aws s3 cp /backups/uploads_*.tar.gz s3://backups-bucket/uploads/
```

### 3. Recovery Procedure

```bash
# Restore database
psql -U ${DB_USER} word_analyzer < /backups/db_20240101.sql

# Restore uploads
tar -xzf /backups/uploads_20240101.tar.gz -C ./
```

---

## CI/CD Pipeline (GitHub Actions)

### `.github/workflows/deploy.yml`

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Build Docker image
      run: docker build -t word-analyzer:latest .
    
    - name: Push to registry
      run: |
        docker login -u ${{ secrets.DOCKER_USER }} -p ${{ secrets.DOCKER_PASS }}
        docker push word-analyzer:latest
    
    - name: Deploy to production
      env:
        DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
      run: |
        mkdir -p ~/.ssh
        echo "$DEPLOY_KEY" > ~/.ssh/id_rsa
        chmod 600 ~/.ssh/id_rsa
        ssh -i ~/.ssh/id_rsa deploy@prod.example.com 'cd /app && docker-compose pull && docker-compose up -d'
```

---

## Scaling Strategy

### Horizontal Scaling

1. **API Servers**: Use load balancer (Nginx, HAProxy)
2. **Database**: PostgreSQL replication/clustering
3. **Spark Cluster**: Add executor nodes
4. **Cache**: Redis cluster
5. **Files**: S3 storage

### Vertical Scaling

1. **Increase server resources** (CPU, RAM)
2. **Optimize PySpark memory** allocation
3. **Add database indexes** for queries
4. **Cache hot data** in Redis

### Auto-scaling (K8s)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: word-analyzer-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: word-analyzer-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Rollback Procedure

### Docker Rollback

```bash
# Check recent images
docker images | head -5

# Revert to previous version
docker-compose down
docker pull word-analyzer:previous-tag
docker-compose up -d
```

### K8s Rollback

```bash
# Check rollout history
kubectl rollout history deployment/word-analyzer-api

# Rollback to previous version
kubectl rollout undo deployment/word-analyzer-api

# Rollback to specific revision
kubectl rollout undo deployment/word-analyzer-api --to-revision=2
```

---

## Maintenance Windows

### Schedule

- **Database maintenance**: 2-4 AM UTC
- **OS updates**: 1st Sunday of month at 3 AM
- **Application updates**: 2nd Wednesday of month
- **Cache cleanup**: Daily at 4 AM

### Procedure

1. Notify users (24-hour notice)
2. Set maintenance mode
3. Perform updates
4. Run tests
5. Restore service
6. Monitor for errors

---

## Incident Response

### Database Down

```bash
# Check status
systemctl status postgresql

# Check logs
tail -f /var/log/postgresql/postgresql.log

# Restart
systemctl restart postgresql

# Verify
psql -U postgres -c "SELECT 1"
```

### API Unresponsive

```bash
# Check processes
ps aux | grep uvicorn

# Check logs
docker logs word-analyzer-api

# Restart
docker-compose restart api

# Scale up if high load
docker-compose up -d --scale api=5
```

### Disk Space Low

```bash
# Check usage
df -h

# Find large files
find . -type f -size +100M

# Clean old logs
find ./logs -mtime +30 -delete

# Clean docker cache
docker system prune -a
```

---

## Related Documentation

- [SETUP.md](SETUP.md) - Installation & configuration
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [API.md](API.md) - API endpoints
- [DATABASE.md](DATABASE.md) - Database administration
