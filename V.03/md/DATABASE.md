# Database Schema Documentation

## Overview

The Word Intelligence Platform uses SQLAlchemy ORM with SQLite (development) and PostgreSQL (production) backend.

**Database File**: `analytics.db` (auto-created on `init_db()`)

**Schema**: 3 main tables (Analysis, User, SparkJob)

---

## Table: analysis

**Purpose**: Store all text analysis records and results

**SQL Definition**:
```sql
CREATE TABLE analysis (
  id VARCHAR NOT NULL,
  input_type VARCHAR NOT NULL,
  input_metadata JSON NOT NULL,
  status VARCHAR NOT NULL,
  raw_data TEXT,
  processed_data JSON,
  visualization_data JSON,
  execution_time FLOAT,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  
  PRIMARY KEY (id)
);

-- Recommended indexes
CREATE INDEX idx_input_type ON analysis(input_type);
CREATE INDEX idx_status ON analysis(status);
CREATE INDEX idx_created_at ON analysis(created_at);
```

**Columns**:

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| id | String (UUID) | NO | uuid4() | Unique analysis identifier |
| input_type | String | NO | - | "file" or "url" |
| input_metadata | JSON | NO | {} | File/URL metadata (filename, size, url, etc.) |
| status | String | NO | "processing" | "processing", "completed", "failed" |
| raw_data | Text | YES | NULL | Extracted text content from file/URL |
| processed_data | JSON | YES | NULL | Analysis results (metrics, statistics) |
| visualization_data | JSON | YES | NULL | Chart data for frontend rendering |
| execution_time | Float | YES | NULL | Analysis execution time in seconds |
| created_at | DateTime | NO | NOW() | Record creation timestamp |
| updated_at | DateTime | NO | NOW() | Last update timestamp (auto-update) |

**Sample Record**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "input_type": "file",
  "input_metadata": {
    "filename": "document.txt",
    "size": 50000,
    "upload_time": "2024-01-15T10:30:00Z"
  },
  "status": "completed",
  "raw_data": "Lorem ipsum dolor sit amet...",
  "processed_data": {
    "total_words": 5234,
    "unique_words": 1456,
    "average_word_length": 4.23,
    "sentiment_score": 6.5,
    "top_words": [
      {"word": "the", "count": 245},
      {"word": "and", "count": 189}
    ],
    "length_distribution": [
      {"length": 1, "count": 234},
      {"length": 2, "count": 456}
    ]
  },
  "visualization_data": {
    "word_frequency": {...},
    "sentiment_pie": {...}
  },
  "execution_time": 1.234,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:02Z"
}
```

**Relationships**:
- One-to-many: `Analysis` → `SparkJob` (analysis_id)

**Queries**:

Get recent analyses:
```sql
SELECT * FROM analysis
ORDER BY created_at DESC
LIMIT 10;
```

Get completed analyses by type:
```sql
SELECT * FROM analysis
WHERE input_type = 'file' AND status = 'completed'
ORDER BY created_at DESC;
```

Count analyses by status:
```sql
SELECT status, COUNT(*) as count
FROM analysis
GROUP BY status;
```

Get analyses between dates:
```sql
SELECT * FROM analysis
WHERE created_at BETWEEN '2024-01-01' AND '2024-01-31'
ORDER BY created_at DESC;
```

---

## Table: user

**Purpose**: Store user accounts and authentication data

**SQL Definition**:
```sql
CREATE TABLE "user" (
  id VARCHAR NOT NULL,
  username VARCHAR NOT NULL UNIQUE,
  email VARCHAR NOT NULL UNIQUE,
  hashed_password VARCHAR NOT NULL,
  is_active BOOLEAN NOT NULL,
  total_analyses INTEGER NOT NULL,
  last_login DATETIME,
  created_at DATETIME NOT NULL,
  
  PRIMARY KEY (id),
  UNIQUE (username),
  UNIQUE (email)
);

-- Recommended indexes
CREATE INDEX idx_username ON "user"(username);
CREATE INDEX idx_email ON "user"(email);
CREATE INDEX idx_is_active ON "user"(is_active);
```

**Columns**:

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| id | String (UUID) | NO | uuid4() | Unique user identifier |
| username | String | NO | - | Unique username |
| email | String | NO | - | Unique email address |
| hashed_password | String | NO | - | bcrypt-hashed password |
| is_active | Boolean | NO | true | User account active status |
| total_analyses | Integer | NO | 0 | Count of user's analyses |
| last_login | DateTime | YES | NULL | Last login timestamp |
| created_at | DateTime | NO | NOW() | Account creation timestamp |

**Sample Record**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "email": "john@example.com",
  "hashed_password": "$2b$12$...",
  "is_active": true,
  "total_analyses": 42,
  "last_login": "2024-01-15T09:45:00Z",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Relationships**:
- One-to-many: `User` → `Analysis` (user_id) [future implementation]

**Queries**:

Get active users:
```sql
SELECT * FROM "user" WHERE is_active = TRUE;
```

Get top users by analysis count:
```sql
SELECT username, total_analyses
FROM "user"
WHERE is_active = TRUE
ORDER BY total_analyses DESC
LIMIT 10;
```

Find user by username:
```sql
SELECT * FROM "user" WHERE username = 'john_doe';
```

---

## Table: spark_job

**Purpose**: Track PySpark job execution and status

**SQL Definition**:
```sql
CREATE TABLE spark_job (
  id VARCHAR NOT NULL,
  analysis_id VARCHAR NOT NULL,
  job_id VARCHAR NOT NULL,
  status VARCHAR NOT NULL,
  metrics JSON,
  logs TEXT,
  created_at DATETIME NOT NULL,
  completed_at DATETIME,
  
  PRIMARY KEY (id),
  FOREIGN KEY (analysis_id) REFERENCES analysis(id)
);

-- Recommended indexes
CREATE INDEX idx_analysis_id ON spark_job(analysis_id);
CREATE INDEX idx_status ON spark_job(status);
CREATE INDEX idx_created_at ON spark_job(created_at);
```

**Columns**:

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| id | String (UUID) | NO | uuid4() | Unique job record identifier |
| analysis_id | String FK | NO | - | Reference to Analysis record |
| job_id | String | NO | - | Spark application job ID |
| status | String | NO | "pending" | "pending", "running", "completed", "failed" |
| metrics | JSON | YES | NULL | Job execution metrics (time, tasks, etc.) |
| logs | Text | YES | NULL | Job execution logs |
| created_at | DateTime | NO | NOW() | Job submission timestamp |
| completed_at | DateTime | YES | NULL | Job completion timestamp |

**Sample Record**:
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "job_id": "app-20240115-001234",
  "status": "completed",
  "metrics": {
    "duration_seconds": 1.234,
    "total_tasks": 8,
    "completed_tasks": 8,
    "failed_tasks": 0,
    "total_word_count": 5234,
    "unique_words": 1456,
    "processing_rate": "4235 words/sec"
  },
  "logs": "2024-01-15 10:30:00 - Job started\n2024-01-15 10:30:01 - Tasks scheduled...",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:02Z"
}
```

**Relationships**:
- Many-to-one: `SparkJob` → `Analysis` (analysis_id)

**Queries**:

Get job status:
```sql
SELECT status, COUNT(*) as count
FROM spark_job
GROUP BY status;
```

Get jobs for specific analysis:
```sql
SELECT * FROM spark_job
WHERE analysis_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY created_at DESC;
```

Get failed jobs:
```sql
SELECT * FROM spark_job
WHERE status = 'failed'
ORDER BY created_at DESC;
```

Calculate average job duration:
```sql
SELECT AVG(CAST((julianday(completed_at) - julianday(created_at)) * 86400 AS FLOAT)) as avg_duration_seconds
FROM spark_job
WHERE status = 'completed';
```

---

## Database Operations

### Initialize Database

```python
from backend.db.database import init_db

# Create all tables
init_db()
```

### Create Session

```python
from backend.db.database import SessionLocal

# Get database session
db = SessionLocal()

# Use session
try:
    # perform operations
    pass
finally:
    db.close()
```

### Insert Record

```python
from backend.models.analysis import Analysis

analysis = Analysis(
    input_type="file",
    input_metadata={"filename": "doc.txt"},
    status="processing"
)
db.add(analysis)
db.commit()
db.refresh(analysis)
```

### Query Records

```python
# Get all
analyses = db.query(Analysis).all()

# Filter
completed = db.query(Analysis).filter(Analysis.status == "completed").all()

# Get one
analysis = db.query(Analysis).filter(Analysis.id == "123").first()

# Paginate
page = db.query(Analysis).offset(0).limit(20).all()

# Count
total = db.query(Analysis).count()

# Order
recent = db.query(Analysis).order_by(Analysis.created_at.desc()).limit(10).all()
```

### Update Record

```python
analysis = db.query(Analysis).filter(Analysis.id == "123").first()
analysis.status = "completed"
analysis.execution_time = 1.234
db.commit()
```

### Delete Record

```python
analysis = db.query(Analysis).filter(Analysis.id == "123").first()
db.delete(analysis)
db.commit()
```

---

## Migration from SQLite to PostgreSQL

### 1. Update .env
```
DATABASE_URL=postgresql://user:password@localhost:5432/word_analyzer
```

### 2. Install PostgreSQL driver
```bash
pip install psycopg2-binary
```

### 3. Backup SQLite
```bash
cp analytics.db analytics.db.backup
```

### 4. Export data (if needed)
```python
# Export from SQLite
sqlite_data = db.query(Analysis).all()

# Import to PostgreSQL
for record in sqlite_data:
    db.add(record)
db.commit()
```

### 5. Reinitialize
```python
from backend.db.database import init_db
init_db()  # Creates PostgreSQL tables
```

---

## Backup & Recovery

### Backup SQLite Database
```bash
# Simple file copy
cp analytics.db analytics.db.backup.$(date +%Y%m%d_%H%M%S)

# Or use sqlite3 CLI
sqlite3 analytics.db ".backup analytics.db.backup"
```

### Restore from Backup
```bash
cp analytics.db.backup analytics.db
```

### Export Data as JSON
```python
import json
from sqlalchemy.orm import Session
from backend.models.analysis import Analysis

db = Session(...)
analyses = db.query(Analysis).all()

data = [
    {
        "id": a.id,
        "input_type": a.input_type,
        "status": a.status,
        # ... other fields
    }
    for a in analyses
]

with open("backup.json", "w") as f:
    json.dump(data, f, indent=2, default=str)
```

---

## Performance Optimization

### Add Indexes
```sql
-- Text search optimization
CREATE FULLTEXT INDEX idx_raw_data ON analysis(raw_data);

-- Query optimization
CREATE INDEX idx_input_type_status ON analysis(input_type, status);
CREATE INDEX idx_created_at_status ON analysis(created_at, status);

-- Relationship optimization
CREATE INDEX idx_analysis_id ON spark_job(analysis_id);
```

### Query Statistics
```python
# Check total storage
import os
db_size = os.path.getsize('analytics.db') / (1024*1024)  # MB

# Count records
from backend.models.analysis import Analysis
total = db.query(Analysis).count()

# Average execution time
from sqlalchemy import func
avg_time = db.query(func.avg(Analysis.execution_time)).scalar()
```

### Connection Pooling (Production)
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600
)
```

---

## Common Queries

### Dashboard Summary
```python
from sqlalchemy import func
from backend.models.analysis import Analysis

total_analyses = db.query(func.count(Analysis.id)).scalar()
file_analyses = db.query(func.count(Analysis.id)).filter(Analysis.input_type == "file").scalar()
url_analyses = db.query(func.count(Analysis.id)).filter(Analysis.input_type == "url").scalar()
avg_execution = db.query(func.avg(Analysis.execution_time)).scalar()
recent = db.query(Analysis).order_by(Analysis.created_at.desc()).limit(5).all()
```

### Filter Analyses
```python
def filter_analyses(
    db: Session,
    input_type: str = None,
    status: str = None,
    start_date: str = None,
    end_date: str = None,
    skip: int = 0,
    limit: int = 50
):
    query = db.query(Analysis)
    
    if input_type:
        query = query.filter(Analysis.input_type == input_type)
    if status:
        query = query.filter(Analysis.status == status)
    if start_date:
        query = query.filter(Analysis.created_at >= start_date)
    if end_date:
        query = query.filter(Analysis.created_at <= end_date)
    
    total = query.count()
    items = query.order_by(Analysis.created_at.desc()).offset(skip).limit(limit).all()
    
    return {"items": items, "total": total}
```

### Get Analysis with Related Jobs
```python
from sqlalchemy.orm import joinedload
from backend.models.analysis import Analysis
from backend.models.spark_job import SparkJob

analysis = db.query(Analysis).options(
    joinedload(Analysis.spark_jobs)
).filter(Analysis.id == "123").first()
```

---

## Data Retention Policies

### Archive Old Records
```python
from datetime import datetime, timedelta

# Delete records older than 90 days
cutoff_date = datetime.now() - timedelta(days=90)
db.query(Analysis).filter(Analysis.created_at < cutoff_date).delete()
db.commit()
```

### Archive to External Storage
```python
import json

# Export to file before deletion
old_analyses = db.query(Analysis).filter(
    Analysis.created_at < cutoff_date
).all()

with open(f"archive_{cutoff_date.date()}.json", "w") as f:
    json.dump([{...} for a in old_analyses], f, default=str)

# Then delete
db.query(Analysis).filter(Analysis.created_at < cutoff_date).delete()
```

---

## Monitoring & Health Checks

### Database Health
```python
def check_db_health(db: Session) -> dict:
    try:
        total_analyses = db.query(Analysis).count()
        return {
            "status": "healthy",
            "total_records": total_analyses,
            "timestamp": datetime.now()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
```

### Monitor Growth
```python
# Analyses per day
from sqlalchemy import func, text

daily_counts = db.query(
    func.date(Analysis.created_at),
    func.count(Analysis.id)
).group_by(func.date(Analysis.created_at)).all()
```

---

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [API.md](API.md) - API endpoints using database
- [SETUP.md](SETUP.md) - Database initialization
