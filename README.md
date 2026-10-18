# Word Intelligence (v0.4)

> Production-grade multi-source text analytics, Apache PySpark DataFrame distributed computation, Natural Language Processing, and MySQL historical persistence platform.

Word Intelligence v0.4 converts raw text, documents (`.txt`, `.pdf`, `.docx`), and public webpage URLs into actionable linguistic statistics, word frequency rankings, length distributions, bigram collocations, noun phrase extractions, and sentiment insights, with interactive Chart.js visualizations, CSV export, and persistent MySQL database storage.

---

## Architecture & Technology Stack

- **Frontend**: React 18, React Router v7, Chart.js & React-Chartjs-2, Vite 5, Vanilla CSS Design System with dark glassmorphism aesthetic, Lucide Icons.
- **Backend API**: FastAPI, Uvicorn (ASGI), Pydantic v2 & Pydantic-Settings, Starlette middleware.
- **Big Data Engine**: Apache PySpark 4.2 (DataFrame pipelines, map-reduce aggregations, local execution).
- **NLP Heuristics**: TextBlob, NLTK (Tokenization, Polarity, Subjectivity, Noun Phrase Extraction).
- **Document Parsers**: `pypdf`, `python-docx`, `beautifulsoup4` (with strict SSRF defense & DNS re-validation).
- **Database & Persistence**: MySQL 8.4, SQLAlchemy 2.0 ORM, Alembic schema migrations.
- **Security Hardening**: Sliding window rate limiting, security response headers (`X-Content-Type-Options`, `X-Frame-Options`, `CSP`), path traversal mitigation, and CSV formula injection sanitization.
- **Containerization**: Multi-stage Docker builds, Nginx reverse proxy, Docker Compose.
- **Automated Tests**: 49 unit, integration, and security tests (`pytest`).

---

## Quick Start (Docker Compose - Recommended)

The fastest and most reproducible way to run the entire stack in production mode:

```bash
# 1. Clone or navigate to repository root
cd Word-Count-Analyzer

# 2. Copy environment template
cp .env.example .env

# 3. Build and launch all containerized services (MySQL, FastAPI Backend, React/Nginx Frontend)
docker compose up --build -d
```

The application will be available at:
- **Web UI & Dashboard**: [http://localhost](http://localhost) (Port 80)
- **API Documentation**: [http://localhost/api/v1/docs](http://localhost/api/v1/docs)
- **Health Check**: [http://localhost/health](http://localhost/health)
- **Readiness Probe**: [http://localhost/api/v1/readiness](http://localhost/api/v1/readiness)

To stop services:
```bash
docker compose down
```

---

## Quick Start (Local Development)

### 1. Prerequisites
- Python 3.13+
- Node.js 20+ & npm
- Java 17+ or 21 LTS (for PySpark)
- MySQL 8.0+ running locally on port 3306

### 2. Configure Environment

Copy `.env.example` to `.env` and configure your local MySQL credentials:
```ini
ENVIRONMENT=development
MYSQL_SERVER=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=word_intelligence
SQLALCHEMY_DATABASE_URI=mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@${MYSQL_SERVER}:${MYSQL_PORT}/${MYSQL_DB}
```

Apply database migrations:
```bash
python -m alembic upgrade head
```

### 3. Backend Setup

```bash
# Install dependencies
pip install -r backend/requirements-dev.txt

# Start FastAPI development server
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

Backend endpoints:
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs)
- **Liveness Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Readiness Probe**: [http://127.0.0.1:8000/api/v1/readiness](http://127.0.0.1:8000/api/v1/readiness)

### 4. Frontend Setup

In a separate terminal:
```bash
npm --prefix frontend install
npm --prefix frontend run dev
```

Frontend UI will open at:
- [http://localhost:5173](http://localhost:5173) (Vite proxies `/api` and `/health` requests to `127.0.0.1:8000`).

---

## Running Automated Tests

Run complete pytest test suite (49 automated tests across 9 test modules):
```bash
python -m pytest -s backend/tests
```

Run frontend production build verification:
```bash
npm --prefix frontend run build
```

---

## Project Structure

```text
Word-Count-Analyzer/
├── frontend/                     # React 18 + Vite application
│   ├── public/
│   ├── src/
│   │   ├── components/           # UI components (Charts, Tables, Metrics)
│   │   │   └── layout/           # AppLayout, Sidebar, MobileNav, PageHeader
│   │   ├── hooks/                # Custom React hooks (useHealth, useAnalysis)
│   │   ├── pages/                # Multi-page views (Dashboard, Analyze, Documents, URL, History, Settings)
│   │   ├── services/             # API client (api.js)
│   │   └── styles/               # CSS Design system (index.css)
│   ├── Dockerfile                # Production multi-stage Nginx build
│   ├── nginx.conf                # Nginx reverse proxy configuration
│   └── package.json
├── backend/                      # FastAPI Python application
│   ├── alembic/                  # Version-controlled database schema migrations
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/           # analysis, export, health, history, readiness
│   │   ├── core/                 # config, security (rate limiter, headers)
│   │   ├── db/                   # base, session management
│   │   ├── models/               # SQLAlchemy ORM models (AnalysisHistory)
│   │   ├── schemas/              # Pydantic validation schemas
│   │   └── services/             # analyzer, document_service, url_service, spark_service, history_service
│   ├── tests/                    # 49 unit, integration, and security tests
│   ├── Dockerfile                # Production Python 3.13 + OpenJDK runtime
│   ├── entrypoint.sh             # DB wait, Alembic auto-migration, Uvicorn startup
│   ├── requirements.txt
│   └── requirements-dev.txt
├── docker-compose.yml            # Production container orchestration
├── docker-compose.override.yml.example
├── alembic.ini                   # Alembic configuration
├── .env.example
├── .gitignore
├── ARCHITECTURE.md
├── TASKS.md
├── PROJECT_CONTEXT.md
└── README.md
```

---

## License

MIT License. Designed and implemented for Big Data & NLP Analytics.
