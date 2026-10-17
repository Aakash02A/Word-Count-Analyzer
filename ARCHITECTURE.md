# Word Intelligence v0.4 — System Architecture

## 1. Architectural Overview

Word Intelligence is built on a decoupled, layered full-stack architecture designed for Big Data analytics, NLP processing, and interactive visualization:

```
[ Browser / Client ]
        │
        ▼ (HTTP / JSON / Multipart)
[ React + Vite Frontend (Port 5173) ]
        │
        ▼ (Vite Proxy / CORS /api/v1)
[ FastAPI ASGI Backend (Port 8000) ]
        │
  ┌─────┴─────────────────────────┐
  │                               │
  ▼                               ▼
[ Analytical Services ]   [ NLP & Ingestion ]
  • PySpark DataFrame       • pypdf / python-docx
  • Core Text Analytics     • TextBlob / NLTK
  • Token & Length Stats    • SSRF-Safe URL Fetcher
  │                               │
  └─────┬─────────────────────────┘
        ▼
[ MySQL Persistence / Repositories ]
  • Analysis History & Summaries (Phase 6)
```

## 2. Directory Structure

```text
Word-Count-Analyzer/
├── frontend/                     # React + Vite client
│   ├── public/                   # Static assets
│   ├── src/
│   │   ├── components/           # UI widgets (StatusBadge, SummaryCards, etc.)
│   │   ├── services/             # API client (api.js)
│   │   ├── styles/               # CSS design system (index.css)
│   │   ├── App.jsx               # Application shell & diagnostics
│   │   └── main.jsx              # Application bootstrap
│   ├── package.json              # Frontend dependencies
│   ├── vite.config.js            # Vite configuration & backend proxy
│   └── index.html                # Entry HTML with modern typography
│
├── backend/                      # FastAPI Python backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── dependencies.py   # FastAPI dependency providers
│   │   │   └── routes/
│   │   │       └── health.py     # Health & liveness endpoints
│   │   ├── core/
│   │   │   └── config.py         # Pydantic Settings & environment config
│   │   └── main.py               # Application factory & CORS middleware
│   ├── tests/
│   │   └── test_health.py        # Automated pytest suite
│   ├── requirements.txt          # Production dependencies
│   └── requirements-dev.txt      # Development & testing dependencies
│
├── .env.example                  # Environment configuration template
├── .gitignore                    # Version control exclusion rules
├── ARCHITECTURE.md               # Architecture specification
├── PROJECT_CONTEXT.md            # Primary product and technical requirements
├── TASKS.md                      # Phase implementation task tracker
└── README.md                     # Setup, verification, and run guide
```

## 3. Layer Responsibilities

- **Frontend (React + Vite)**: Handles user interaction, form inputs, live diagnostic polling, rendering analytics, and CSV exports.
- **Backend API (FastAPI)**: Validates incoming requests using Pydantic models, manages CORS, handles routing, and enforces security boundaries.
- **Core Configuration (`app/core/config.py`)**: Environment-based configuration with type-safety and fallback defaults.
- **Analytics Services (Phase 2 & 3)**: Pure computation layer for deterministic token metrics, word frequencies, and PySpark DataFrame processing.
- **Document & Ingestion Services (Phase 4)**: Safely extracts text from files (TXT, PDF, DOCX) and validates URLs with SSRF protection.
- **Persistence Layer (Phase 6)**: SQLAlchemy ORM and Alembic migrations targeting MySQL for analysis history.
