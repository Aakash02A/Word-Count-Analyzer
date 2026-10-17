# Word Intelligence (v0.4)

> Intelligent multi-source text analytics, Big Data DataFrame processing, and Natural Language Processing platform.

Word Intelligence v0.4 converts raw text, documents (TXT, PDF, DOCX), and public webpage URLs into actionable linguistic statistics, word frequency rankings, length distributions, and sentiment insights.

---

## Architecture & Technology Stack

- **Frontend**: React 18, Vite 5, Vanilla CSS Design System with sleek dark aesthetic, Lucide Icons
- **Backend**: FastAPI, Uvicorn (ASGI), Pydantic v2 & Pydantic-Settings
- **Testing**: pytest, pytest-asyncio, HTTPX / Starlette TestClient
- **Planned Stack**: Apache PySpark, TextBlob, NLTK, pypdf, python-docx, MySQL, Docker

---

## Runtime Environment & Compatibility

Verified development environment:
- **Python**: 3.13.14 (Backend virtual environment in `backend/.venv`)
- **Java**: 21.0.12 LTS (Available for PySpark in Phase 3)
- **Node.js**: v24.16.0 / npm 11.13.0
- **Docker**: 29.8.2

---

## Quick Start (Local Development)

### 1. Backend Setup

```bash
# Navigate to backend or workspace root
cd a:\GITHUB\Word-Count-Analyzer

# Activate virtual environment (Windows PowerShell)
.\backend\.venv\Scripts\Activate.ps1

# (Optional) If installing dependencies in a fresh environment:
python -m venv backend/.venv
.\backend\.venv\Scripts\pip.exe install -r backend/requirements-dev.txt

# Run the backend dev server
backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

Backend will be available at:
- **API Root**: `http://127.0.0.1:8000/`
- **Health Endpoint**: `http://127.0.0.1:8000/health`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/api/v1/docs`
- **ReDoc**: `http://127.0.0.1:8000/api/v1/redoc`

---

### 2. Frontend Setup

In a separate terminal:

```bash
cd a:\GITHUB\Word-Count-Analyzer\frontend

# Install dependencies (if not already installed)
npm install

# Start Vite development server
npm run dev
```

Frontend will be available at:
- **UI Dashboard**: `http://127.0.0.1:5173/` (proxies `/api` and `/health` to backend)

---

### 3. Running Automated Tests

Run backend tests using pytest:

```bash
backend\.venv\Scripts\pytest.exe backend\tests -v
```

Run frontend build verification:

```bash
cd frontend
npm run build
```

---

## Project Structure

```text
Word-Count-Analyzer/
├── frontend/                     # React + Vite application
│   ├── public/
│   ├── src/
│   │   ├── components/           # UI components (StatusBadge, etc.)
│   │   ├── services/             # API client (api.js)
│   │   ├── styles/               # CSS Design system (index.css)
│   │   ├── App.jsx               # Main React component & diagnostics
│   │   └── main.jsx              # React bootstrap
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── backend/                      # FastAPI Python application
│   ├── app/
│   │   ├── api/
│   │   │   ├── dependencies.py
│   │   │   └── routes/
│   │   │       └── health.py
│   │   ├── core/
│   │   │   └── config.py
│   │   └── main.py
│   ├── tests/
│   │   └── test_health.py
│   ├── requirements.txt
│   └── requirements-dev.txt
├── .env.example
├── .gitignore
├── ARCHITECTURE.md
├── TASKS.md
├── PROJECT_CONTEXT.md
└── README.md
```

---

## Current Status: Phase 1 Complete

Phase 1 foundation has been established and verified. Awaiting approval to begin **Phase 2 — Core Analytics Engine**.
