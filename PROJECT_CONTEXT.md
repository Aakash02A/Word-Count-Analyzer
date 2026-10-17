# PROJECT_CONTEXT.md
# Word Intelligence v0.4 — Complete Project Specification

**Document type:** Product requirements, technical architecture, implementation rules, and AI coding-agent instructions  
**Project name:** Word Intelligence  
**Version:** 0.4  
**Project type:** Publicly accessible full-stack web application  
**Primary domain:** Big Data Analytics  
**Secondary domains:** Natural Language Processing (NLP), data engineering, document processing, and data visualization  
**Development approach:** Incremental, test-driven where practical, security-conscious, and deployment-oriented

---

## 1. Project Overview

### 1.1 What is Word Intelligence?

Word Intelligence is a full-stack web application that allows users to analyse text and documents through a browser.

Users can submit raw text, upload supported documents, or provide a webpage URL. The system extracts and processes the text, calculates linguistic statistics, performs basic NLP analysis, and presents the results through an interactive dashboard.

The application combines:

- React for the frontend user interface.
- FastAPI for backend APIs.
- Apache PySpark for DataFrame-based text analytics.
- NLTK and TextBlob for NLP.
- MySQL for persistent analysis history.
- Docker for reproducible environments and deployment preparation.

The goal is to produce a real, usable, maintainable public application rather than a collection of disconnected scripts or a local-only demonstration.

### 1.2 Problem statement

Users often need to understand the contents of documents or large blocks of text without manually counting words, identifying common terms, calculating text statistics, or inspecting basic sentiment.

Word Intelligence aims to simplify this process by providing a unified interface that converts supported text sources into structured analytical results and visualizations.

### 1.3 Project objectives

1. Accept text from multiple input sources.
2. Extract readable text from supported documents and webpages.
3. Calculate accurate word-level and phrase-level statistics.
4. Provide basic sentiment and linguistic analysis.
5. Visualize results using interactive charts and tables.
6. Allow users to export analytical results as CSV.
7. Save analysis history in MySQL.
8. Provide a maintainable API and modular backend architecture.
9. Include automated tests and reproducible development instructions.
10. Deploy a working version that can be accessed publicly through a web browser.

### 1.4 What the project is not

Word Intelligence is not intended to be:

- A general-purpose AI chatbot.
- A large language model training platform.
- A complete grammar correction system.
- A plagiarism detection service.
- A document authenticity verification system.
- A distributed Spark cluster management platform.
- An enterprise-scale analytics platform unless future requirements and infrastructure justify that description.

Do not claim capabilities that have not been implemented and tested.

---

## 2. Target Users and Usage

The application should be understandable to students, researchers, developers, content writers, and other users who need basic text analytics.

Typical use cases include:

- Finding the most frequent words in an article.
- Analysing the text extracted from a PDF report.
- Identifying frequently occurring two-word phrases.
- Comparing basic sentiment across different text samples.
- Understanding word-length distributions.
- Extracting text statistics from a webpage.
- Reviewing previously saved analyses.
- Downloading results for use in reports or spreadsheets.

The initial application does not require mandatory user accounts. Do not introduce authentication, user profiles, role management, or subscription systems unless explicitly approved as a later requirement.

If history is available without authentication, disclose that saved analyses may be accessible to other visitors if the system is publicly shared. Prefer privacy-preserving behaviour and avoid storing raw document contents unless necessary and explicitly approved.

---

## 3. Functional Requirements

### FR-01: Raw text input

Users must be able to:

- Paste or type text into a text input area.
- Submit text for analysis.
- See validation errors for empty or oversized input.
- See loading indicators while analysis is running.
- View structured results when analysis completes.
- See readable error messages when processing fails.

### FR-02: Document uploads

Support these file formats:

- TXT
- PDF
- DOCX

The backend must validate file size, permitted file type, and actual content where practical.

Requirements:

- TXT files must be decoded safely.
- PDFs must be processed with `pypdf`.
- DOCX files must be processed with `python-docx`.
- Empty, unreadable, corrupted, or unsupported files must produce controlled errors.
- Scanned PDFs may not contain extractable text. Detect or explain this limitation rather than pretending OCR has occurred.
- Uploaded files must not be stored permanently unless explicitly required.
- Temporary files must be removed after processing.
- File uploads must have configurable size and extracted-text limits.

OCR is outside the initial scope. It can be considered later if a real requirement emerges.

### FR-03: Webpage URL analysis

Users may submit an HTTP or HTTPS URL for text extraction and analysis.

The URL service must:

- Accept only permitted HTTP and HTTPS URLs.
- Reject localhost, private, loopback, link-local, reserved, and internal infrastructure destinations.
- Validate resolved IP addresses and protect against DNS rebinding.
- Revalidate destinations after redirects.
- Apply strict connection and read timeouts.
- Limit response size.
- Reject unsupported content types.
- Avoid executing webpage JavaScript.
- Extract readable text using Beautiful Soup.
- Return understandable errors for inaccessible or invalid pages.

**Security requirement:** URL fetching is an SSRF-sensitive operation. Do not implement a naive `requests.get(user_supplied_url)` endpoint without destination validation, redirect controls, and response limits.

### FR-04: Text preprocessing

Implement a documented and consistent preprocessing pipeline.

Responsibilities:

- Normalize input text where appropriate.
- Handle whitespace and line breaks.
- Tokenize words consistently.
- Support case-insensitive word-frequency analysis by default.
- Handle punctuation and common Unicode text.
- Define whether numeric tokens are included.
- Keep the original text separate from the normalized analytical representation where needed.

Do not remove punctuation, numbers, stopwords, or meaningful tokens indiscriminately. Different analyses may need different representations.

### FR-05: Word statistics

The analysis engine must provide:

1. Total token count.
2. Unique token count.
3. Word-frequency distribution.
4. Most frequent words.
5. Configurable top-N results.
6. Word-length distribution.
7. A clear and consistent tokenization policy.

The API must return machine-readable data rather than preformatted chart images.

For example, word-frequency output may contain:

- `word`
- `count`
- `percentage`, if calculated consistently

Document the meaning of each metric. In particular, distinguish raw input length, total tokens, and unique tokens.

### FR-06: Keyword and stopword analysis

Provide a keyword-frequency view based on token frequency and optional stopword filtering.

Use NLTK stopwords where appropriate, with an explicit strategy for missing or unavailable corpora.

Requirements:

- Support a documented default language.
- Avoid downloading NLP resources silently during every request.
- Provide an installation or initialization procedure for required datasets.
- Handle missing resources with a controlled diagnostic.
- Do not label simple frequency ranking as advanced semantic keyword extraction.

### FR-07: Bigram analysis

Calculate adjacent two-token sequences.

Example:

Input: `java is powerful and java is popular`

The bigram sequence should be determined by the chosen tokenizer and preprocessing rules.

Return the most frequent bigrams with their counts.

The implementation must use a consistent token sequence and must have tests for short text, repeated phrases, punctuation, and empty input.

### FR-08: Word-length distribution

Calculate the frequency of words grouped by length.

Example response:

- Length 2: 4 words
- Length 4: 7 words
- Length 6: 2 words

The actual output must be calculated from input data. Do not use hardcoded demonstration results in production endpoints.

### FR-09: Sentiment analysis

Use TextBlob for basic polarity-based sentiment analysis.

Return a documented result containing:

- Polarity score.
- Optional subjectivity score.
- A derived label such as positive, neutral, or negative.

Define the label thresholds centrally and test them.

Sentiment must be described as a basic heuristic, not a definitive interpretation of meaning, intent, or emotion.

### FR-10: Noun-phrase extraction

Use TextBlob noun-phrase extraction where supported.

Return a list of extracted phrases.

Handle empty text, unsupported language, and NLP-processing failures without crashing the API.

### FR-11: Interactive dashboard

The React dashboard should provide:

- A text input area.
- File-upload controls.
- A URL input field.
- A clear Analyze action.
- Loading, empty, success, and error states.
- Summary cards for key metrics.
- A word-frequency table.
- A word-length chart.
- A bigram-frequency table or chart.
- Sentiment results.
- Extracted noun phrases.
- CSV export.
- Responsive layout for desktop and mobile browsers.

Charts must be generated from API responses, not hardcoded example data.

Choose **one chart library** for the initial implementation: Chart.js or Recharts. Do not install both without a justified requirement.

### FR-12: CSV export

Allow users to export relevant analytical results.

Requirements:

- Include meaningful column headers.
- Use UTF-8 encoding.
- Escape values correctly.
- Prevent CSV formula injection for values that could be interpreted as spreadsheet formulas.
- Use the same analytical values displayed in the dashboard.
- Handle empty results correctly.

A client-side export is acceptable for the initial implementation if it uses validated analysis results. A backend export endpoint can be introduced when justified.

### FR-13: Analysis history

Use MySQL to persist analysis history.

A saved analysis may include:

- Unique analysis ID.
- Source type: text, file, or URL.
- Optional sanitized source label.
- Creation timestamp.
- Analytical summary and structured results, if required.
- Processing status where asynchronous processing is later introduced.

Privacy requirements:

- Do not save raw submitted text or uploaded document contents by default.
- Do not save credentials, cookies, authorization headers, or sensitive URL query parameters.
- Avoid retaining personal data unnecessarily.
- Document history retention and deletion behaviour.
- Do not expose one user's private data to another user.

The initial version may implement history only after core analysis is verified. Do not let history requirements block a working analysis pipeline.

---

## 4. Technology Stack

Use the following technologies unless a documented compatibility issue requires an approved change.

### Frontend

- React
- JavaScript ES6+
- Vite
- HTML5
- CSS3
- Chart.js or Recharts
- Browser Fetch API
- Vitest for frontend unit tests when appropriate
- ESLint for frontend linting

TypeScript is not required for the initial version. Do not convert the project to TypeScript without approval.

### Backend

- Python
- FastAPI
- Uvicorn for ASGI serving
- Pydantic for API schemas and validation
- HTTPX for API integration testing
- Ruff for linting and formatting
- pytest for automated tests

### Analytics and NLP

- Apache PySpark
- NLTK
- TextBlob
- Python standard library, including `re` and `collections`

Use additional libraries only when a real requirement justifies them.

### Database

- MySQL
- SQLAlchemy
- Alembic
- PyMySQL as the database driver

SQLite is an acceptable fallback for a development-only implementation if MySQL cannot be configured immediately, but it must not be introduced silently or treated as the approved production database.

### Document and webpage processing

- `pypdf`
- `python-docx`
- HTTPX or `requests`
- Beautiful Soup 4

Choose a consistent HTTP client for backend URL fetching. Avoid maintaining two clients without a specific need.

### Infrastructure

- Git
- GitHub
- Docker
- Docker Compose
- GitHub Actions for CI
- A production-compatible ASGI deployment setup
- A cloud host that supports the selected Python, Java, Spark, memory, and storage requirements

Pin compatible dependency versions and maintain reproducible installation instructions.

---

## 5. High-Level Architecture

The application follows a layered architecture.

### Request flow

1. A user interacts with the React frontend.
2. The frontend sends an HTTP request to FastAPI.
3. The API validates the request using Pydantic and dedicated validators.
4. A route invokes the appropriate service.
5. Document or URL services extract text when necessary.
6. The analysis service applies the preprocessing and analytics pipeline.
7. PySpark performs the selected DataFrame-based analytical operations.
8. NLP services calculate sentiment and noun phrases.
9. The repository layer persists approved metadata and results.
10. FastAPI returns a validated JSON response.
11. React renders the results and charts.

### Layer responsibilities

**API routes**

- Receive requests.
- Validate and coordinate operations.
- Call service methods.
- Return structured responses.
- Convert known failures into suitable HTTP errors.

Routes must not contain the full analysis implementation.

**Schemas**

- Define request models.
- Define response models.
- Validate field types, limits, and expected formats.
- Keep API contracts stable and documented.

**Services**

- Contain application and business logic.
- Coordinate extraction, preprocessing, analytics, and NLP.
- Remain independent of frontend rendering.

**Repositories**

- Contain database query operations.
- Encapsulate persistence.
- Avoid embedding database queries inside API routes or analytics algorithms.

**Database layer**

- Manage SQLAlchemy engine and session creation.
- Manage database lifecycle and transaction boundaries.
- Read connection settings from environment-based configuration.

**Core configuration**

- Load and validate environment variables.
- Store runtime settings and configurable limits.
- Avoid hardcoded credentials.

**Middleware**

- Add only justified request-processing concerns.
- Configure CORS explicitly.
- Avoid broad middleware that obscures errors or changes behaviour unexpectedly.

---

## 6. Required Repository Structure

Use this structure as the target architecture.

```text
word-intelligence/
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   └── Dashboard.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── hooks/
│   │   ├── styles/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── health.py
│   │   │       ├── analysis.py
│   │   │       ├── documents.py
│   │   │       ├── urls.py
│   │   │       └── history.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── analyzer.py
│   │   │   ├── spark_service.py
│   │   │   ├── document_service.py
│   │   │   ├── nlp_service.py
│   │   │   └── url_service.py
│   │   ├── repositories/
│   │   │   └── history_repository.py
│   │   ├── db/
│   │   │   ├── session.py
│   │   │   └── base.py
│   │   └── middleware/
│   ├── tests/
│   │   ├── test_health.py
│   │   ├── test_analysis.py
│   │   ├── test_documents.py
│   │   ├── test_urls.py
│   │   ├── test_api.py
│   │   └── test_validators.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── alembic.ini
│
├── database/
│   ├── migrations/
│   └── seed.py
│
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── PROJECT_CONTEXT.md
├── ARCHITECTURE.md
├── TASKS.md
└── README.md
```

This is the intended structure, not a requirement to create every file immediately. Create files when the relevant implementation phase needs them. Avoid empty placeholder modules and unnecessary abstractions.

The `frontend` and `backend` directories must have independent dependency manifests.

Use the actual Alembic environment and migration scripts for schema management. Keep the `database/migrations/` directory as the documented project-level migration location only if the configured migration setup genuinely uses it; do not create competing migration systems.

---

## 7. API Contract

All API responses must use consistent JSON structures and appropriate HTTP status codes.

Use a versioned API prefix such as `/api/v1` for application endpoints.

### Health

`GET /health`

Purpose:

- Confirm that the API process is running.
- Return a simple JSON status.
- Avoid exposing credentials, internal paths, or sensitive configuration.

A separate readiness endpoint may check required dependencies such as MySQL. Do not make basic liveness depend on the database being available.

### Analyse raw text

`POST /api/v1/analysis`

Example request:

```json
{
  "text": "Java is powerful. Java is popular.",
  "top_n": 10
}
```

The schema may evolve, but validation must reject empty or oversized text and invalid `top_n` values.

### Analyse an uploaded file

`POST /api/v1/analysis/file`

Use multipart form data with the uploaded file and supported options.

Return the same core analysis schema used for raw text wherever possible.

### Analyse a webpage

`POST /api/v1/analysis/url`

Example request:

```json
{
  "url": "https://example.com"
}
```

This endpoint must use the secure URL-fetching service. Never bypass URL validation.

### Analysis history

`GET /api/v1/history`

Return a paginated history list, with safe defaults and maximum page sizes.

`GET /api/v1/history/{analysis_id}`

Return one saved analysis only if it is accessible under the application's privacy and authorization policy.

History deletion can be added when the persistence layer is implemented.

### Response design

Use a consistent result structure containing appropriate fields for:

- Analysis ID, when persisted.
- Source type.
- Processing metadata where useful.
- Token counts.
- Unique token counts.
- Word frequencies.
- Word-length distribution.
- Bigrams.
- Keywords.
- Sentiment.
- Noun phrases.

Use Pydantic response models. Do not expose SQLAlchemy objects directly as API responses.

### Error responses

Errors must be structured and understandable.

Handle at least:

- Empty input.
- Invalid input.
- Unsupported file format.
- Oversized upload.
- Corrupted document.
- Empty extracted text.
- Invalid or blocked URL.
- Network timeout.
- Analysis failure.
- Database failure.

Do not return stack traces, credentials, or internal exception details to public clients.

---

## 8. PySpark Design and Performance

PySpark is included because data processing and big-data analytics are important parts of the project.

However, PySpark introduces Java compatibility requirements, startup latency, memory overhead, and lifecycle concerns.

### Required principles

1. Keep Spark-specific logic inside `spark_service.py` or another explicitly documented Spark module.
2. Do not create a new Spark session for every API request.
3. Manage Spark initialization and shutdown through a clear application lifecycle.
4. Avoid launching multiple Spark contexts accidentally.
5. Do not expose the Spark UI publicly.
6. Do not collect large datasets into Python memory without an explicit limit.
7. Avoid using Spark for trivial operations merely to claim big-data functionality.
8. Keep the analytics service independent of the API transport layer.
9. Test the numerical correctness of Spark results against known expected results.
10. Record benchmark methodology and actual results if performance claims are made.

### Initial execution model

Start with local Spark execution using a compatible Java runtime and a single-machine environment.

Evaluate whether PySpark should handle all statistics or only the DataFrame-oriented processing operations. Simple tokenization, short text operations, and small aggregations may be better handled directly in Python.

Document the decision and benchmark it where practical.

Do not claim that the application is distributed, cluster-based, or enterprise-scale merely because it uses PySpark.

### Runtime compatibility

Before implementing Spark integration:

- Inspect the installed Python version.
- Inspect the installed Java version.
- Select compatible PySpark and Java versions.
- Verify that the selected versions work together.
- Verify that the deployment host supports the required runtime.
- Document memory and startup limitations.

Do not upgrade or downgrade installed runtimes blindly.

---

## 9. MySQL and Data Persistence

MySQL is the selected database for the project.

Use SQLAlchemy to isolate database access from business logic and Alembic to manage schema changes.

### Database principles

- Use environment-based connection configuration.
- Use SQLAlchemy sessions with explicit lifecycle management.
- Use parameterized queries and ORM operations.
- Apply transactions where multiple writes must succeed together.
- Define indexes and constraints according to actual query patterns.
- Avoid storing large raw document contents by default.
- Never commit database credentials.
- Do not use automatic production schema mutation as a substitute for migrations.
- Keep schema changes version-controlled.

### Initial history model

An analysis-history record may include:

- Primary key.
- Source type.
- Sanitized source label.
- Creation timestamp.
- Processing status, if applicable.
- Structured results or a documented reference to stored results.

Select JSON storage, normalized tables, or a combination based on query requirements. Do not create many tables without a concrete reason.

### Database startup

A missing or invalid database configuration must produce a clear diagnostic.

Do not silently switch from MySQL to SQLite when a connection fails. This can lead to data being written to an unexpected database.

Provide documented development setup instructions, migration commands, and a controlled way to initialize an empty database.

---

## 10. Frontend Design Requirements

The frontend must be a real React application, not a static HTML page pretending to be a React implementation.

### Component responsibilities

`App.jsx`

- Defines the overall application composition and routing if routing is introduced.

`main.jsx`

- Initializes React and mounts the application.

`pages/`

- Contains page-level components such as the home and dashboard views.

`components/`

- Contains reusable UI elements such as upload controls, summary cards, charts, tables, and status messages.

`services/api.js`

- Centralizes backend HTTP requests.
- Handles API base URL configuration.
- Parses JSON and handles failed HTTP responses.
- Does not contain analytical business logic.

`hooks/`

- Contains reusable React hooks when a real reuse case exists.

`styles/`

- Contains organized CSS.

### User experience requirements

- Clear navigation and page structure.
- Responsive desktop and mobile layout.
- Accessible form labels and controls.
- Visible loading and failure states.
- Useful validation messages.
- No fake data presented as real results.
- No broken controls or inert buttons.
- No unnecessary animation or UI libraries.
- Consistent presentation of all analytical metrics.

### Frontend-backend connection

Use a configurable API base URL.

During local development, configure Vite's proxy where useful to avoid unnecessary CORS complications.

In production, prefer a same-origin deployment where practical. If frontend and backend are deployed on different origins, configure CORS using an explicit allowlist rather than wildcard access.

Never put database passwords, API secrets, or other private credentials into frontend environment variables.

---

## 11. Security Requirements

Security is part of implementation, not a final cosmetic phase.

### Input and upload security

- Enforce configurable request-size limits.
- Enforce file-size and extracted-text limits.
- Validate allowed file formats.
- Treat filenames as untrusted input.
- Store temporary files safely.
- Clean up temporary files.
- Handle corrupted documents without exposing internal errors.

### URL-fetching security

- Reject internal and prohibited IP ranges.
- Validate DNS resolution.
- Revalidate redirect destinations.
- Prevent access to cloud metadata endpoints and internal services.
- Apply timeouts and response-size limits.
- Avoid forwarding application credentials to requested websites.

### Database security

- Use parameterized SQL and ORM operations.
- Restrict database account permissions.
- Avoid public exposure of the database port.
- Protect connection credentials.
- Use transactions and predictable session cleanup.

### Browser security

- Avoid unsafe HTML injection.
- Render submitted text as text rather than executable HTML.
- Sanitize or safely render extracted webpage content.
- Configure CORS appropriately.
- Add suitable security headers at the application or deployment layer.

### CSV security

- Escape CSV values correctly.
- Mitigate spreadsheet formula injection.
- Do not assume that quoting a field alone always makes it safe.

### Secrets and configuration

- Commit `.env.example` with placeholders only.
- Ignore actual `.env` files.
- Never hardcode passwords, tokens, or production credentials.
- Do not log raw submitted documents or sensitive query parameters.

### Operational security

- Do not expose the Spark UI publicly.
- Do not run the Flask development server; this project uses FastAPI.
- Do not run the Uvicorn development configuration as the production deployment without evaluating the required production setup.
- Apply request timeouts, concurrency limits, and resource limits appropriate to the host.
- Add rate limiting or equivalent abuse controls before public launch where required.

---

## 12. Configuration and Environment

Use environment variables for deployment-specific settings.

`.env.example` should document the required configuration without containing real credentials.

Possible settings include:

- Application environment.
- API base configuration.
- MySQL connection URL or individual connection settings.
- Allowed frontend origins.
- Maximum upload size.
- Maximum extracted-text length.
- HTTP connection and read timeouts.
- Spark master and runtime settings.
- History-retention configuration.

Use a configuration module based on Pydantic Settings or an equivalent typed configuration approach.

Validate configuration at startup and provide actionable errors for missing required settings.

Avoid loading secrets into frontend build variables.

---

## 13. Docker and Deployment

The final application must be deployable and accessible publicly.

### Development

Docker Compose should eventually support the required services, such as:

- React/Vite development service when containerized development is useful.
- FastAPI backend.
- MySQL database.

Local development may also run React and FastAPI directly on the host. Docker should not be forced into every development action.

### Production

The production configuration must:

- Build the frontend into static assets.
- Serve frontend assets through a suitable web server, CDN, or configured same-origin application deployment.
- Run FastAPI using a production-compatible ASGI setup.
- Use a compatible Python and Java runtime for PySpark.
- Provide sufficient memory for Spark and document processing.
- Connect to a persistent MySQL instance.
- Keep secrets in hosting environment configuration.
- Enable HTTPS.
- Keep database and Spark administrative interfaces private.
- Provide health checks and useful logs.
- Avoid relying on ephemeral container filesystems for persistent database data.

Do not assume that a hosting platform supports PySpark or Java simply because it supports Python containers.

### Deployment verification

The project is not considered deployed merely because Docker builds successfully.

Verify:

1. The frontend URL loads from an external browser.
2. The API health endpoint is accessible as intended.
3. The frontend can call the production API.
4. A real analysis request succeeds.
5. A supported document can be processed.
6. MySQL persistence works if history is enabled.
7. A failed request produces a controlled response.
8. HTTPS and allowed-origin configuration work.
9. The application stays within the selected host's resource limits.
10. The actual public URL is documented.

---

## 14. Testing Strategy

Use automated tests throughout implementation.

### Unit tests

Test:

- Tokenization.
- Text normalization.
- Total and unique token counts.
- Word frequencies.
- Keyword filtering.
- Bigrams.
- Word-length distribution.
- Sentiment labels.
- Noun-phrase handling.
- Input validation.
- File validation.
- URL validation.

### Integration tests

Test:

- FastAPI endpoint responses.
- Request and response schemas.
- Service-to-service interactions.
- Database persistence.
- Repository operations.
- Database error handling.
- File-upload processing.
- Mocked webpage fetching.
- Correct HTTP error codes.

### Frontend tests

Where useful, test:

- Form validation.
- API service behaviour.
- Loading and error states.
- Result rendering.
- Chart input data.
- CSV export.

### Security tests

Test prohibited URL destinations, redirect handling, oversized files, malformed requests, and attempts to inject executable HTML or CSV formulas.

Use mocks for external network calls. Tests must not depend on arbitrary public websites being available.

### Test honesty

- Never claim a test passed unless it was actually executed.
- Never replace a failing test with a hardcoded success.
- Never remove an existing test simply to make the suite green.
- Investigate failures and report unresolved problems.
- Separate tests that passed from tests that could not run because a dependency or environment was unavailable.

---

## 15. Development Phases

Implement the application in the following order.

### Phase 0 — Repository inspection and planning

- Inspect existing repository contents.
- Identify existing work that must be preserved.
- Check installed Python, Java, Node.js, npm, Docker, and MySQL versions.
- Review runtime compatibility.
- Review existing tests and configuration.
- Document important constraints.
- Avoid destructive changes.

**Completion:** a short environment and compatibility report exists.

### Phase 1 — Foundation

- Create the agreed repository structure.
- Initialize React with Vite.
- Create the FastAPI application.
- Add configuration handling.
- Add a health endpoint.
- Configure local frontend-backend communication.
- Add initial automated tests.
- Document startup commands.

**Completion:** frontend and backend start successfully, health checks work, and initial tests pass.

### Phase 2 — Core analytics

- Implement preprocessing and tokenization.
- Implement word counts and unique counts.
- Implement word frequencies.
- Implement bigrams and word-length distribution.
- Add API schemas and endpoints.
- Add tests for normal and edge cases.

**Completion:** known input produces verified analytical results.

### Phase 3 — PySpark integration

- Select compatible versions.
- Implement controlled Spark lifecycle management.
- Integrate the selected analytical operations.
- Compare Spark output with known expected results.
- Benchmark startup and processing where practical.
- Document runtime limitations.

**Completion:** Spark integration works reliably without uncontrolled session creation.

### Phase 4 — Documents and NLP

- Add TXT, PDF, and DOCX extraction.
- Add file validation and resource limits.
- Add URL extraction and SSRF protections.
- Add NLTK preprocessing.
- Add TextBlob sentiment and noun phrases.
- Add focused tests.

**Completion:** supported sources are processed correctly, and failures are handled safely.

### Phase 5 — React dashboard

- Build the input interface.
- Add reusable components.
- Connect the API service.
- Display summary metrics and analytical results.
- Add charts and tables.
- Add CSV export.
- Add loading, empty, and error states.
- Verify responsive behaviour.

**Completion:** users can analyse text and see actual backend results through the UI.

### Phase 6 — Database and history

- Configure MySQL.
- Add SQLAlchemy session management.
- Add models and repositories.
- Configure Alembic migrations.
- Persist analysis metadata and results.
- Add history endpoints and pagination.
- Verify data isolation and retention requirements.

**Completion:** saved history survives application restarts and is not exposed improperly.

### Phase 7 — Hardening and quality

- Complete input validation.
- Review SSRF and upload protections.
- Review database permissions.
- Review error handling and logging.
- Add appropriate abuse controls.
- Run automated tests.
- Remove debug settings and unused dependencies.
- Document remaining risks.

**Completion:** critical defects are addressed and the release candidate is verified.

### Phase 8 — Public deployment

- Build production frontend assets.
- Prepare the backend deployment.
- Configure persistent MySQL.
- Configure runtime environment variables.
- Deploy to compatible hosting.
- Configure HTTPS.
- Test real public requests.
- Document the public URL and operational limitations.

**Completion:** the public website works from a browser outside the development environment.

---

## 16. Coding Standards

The agent must follow these rules.

1. Prefer clear, readable implementations over clever abstractions.
2. Use descriptive variable and function names.
3. Keep functions focused on one responsibility.
4. Separate routes, schemas, services, repositories, and configuration.
5. Avoid circular imports.
6. Avoid unnecessary global state.
7. Manage database sessions and temporary files predictably.
8. Use type hints for Python functions and public service interfaces.
9. Use Pydantic models for API contracts.
10. Keep configuration separate from business logic.
11. Avoid duplicated analytical algorithms.
12. Avoid unused dependencies and empty placeholder modules.
13. Do not hardcode example analytical results.
14. Do not add authentication, caching, queues, microservices, or cloud infrastructure without an approved requirement.
15. Do not introduce a second database or charting library without justification.
16. Keep documentation aligned with the actual implementation.
17. Prefer small changes that are easy to test and review.
18. Preserve working code unless a change is justified.
19. Explain important compatibility or architecture decisions.
20. Do not silently change the approved technology stack.

---

## 17. AI Coding-Agent Operating Rules

This section is mandatory for every coding agent working on the project.

### Before editing

1. Read this entire `PROJECT_CONTEXT.md`.
2. Inspect the current repository.
3. Read relevant existing source files and documentation.
4. Identify the current phase and its completion criteria.
5. Check available runtimes and installed dependencies.
6. Identify potential compatibility problems.
7. Prepare a short implementation plan.
8. Identify files that will be created or changed.

Do not assume the repository is empty. Do not delete existing files without understanding their purpose.

### During implementation

1. Work only on the authorized phase.
2. Implement the smallest complete solution for that phase.
3. Follow the approved directory structure.
4. Avoid unrelated refactoring.
5. Add tests alongside new functionality.
6. Run the relevant tests and commands.
7. Investigate failures rather than hiding them.
8. Document necessary environment changes.
9. Never put real credentials into source control.
10. Never claim functionality exists when it is only planned.

### After implementation

Provide a concise report containing:

- Phase completed.
- Files created.
- Files modified.
- Important decisions.
- Commands executed.
- Actual test results.
- Tests not run and why.
- Known limitations.
- Security concerns that remain.
- Exact commands for the next developer to run.
- Recommended next step.

### Phase boundaries

Do not proceed to the next phase automatically.

After completing and reporting a phase, wait for approval before making substantial changes for the following phase.

If a blocking issue is found, explain it and propose the smallest safe resolution instead of making an unrelated architectural change.

### Handling uncertainty

If a requirement is ambiguous:

- Follow the documented requirements where possible.
- Choose the simplest safe implementation for reversible details.
- Document assumptions.
- Ask one focused question when an unresolved decision materially affects security, data loss, cost, compatibility, or architecture.

Do not ask the user to make decisions that can be resolved through repository inspection or straightforward testing.

---

## 18. Definition of Done

A phase is complete only when its relevant requirements are implemented and verified.

A task is not complete merely because source code has been generated.

The final product should satisfy these conditions:

- React frontend and FastAPI backend work together.
- The analytics engine returns correct results for verified inputs.
- Supported documents are processed with appropriate limits.
- URL fetching includes SSRF protections.
- PySpark integration is controlled and tested.
- NLP failures are handled safely.
- MySQL persistence and migrations work when history is enabled.
- The frontend displays real analytical results.
- CSV export produces valid and appropriately sanitized data.
- Automated tests cover important behaviour and edge cases.
- Secrets are excluded from source control.
- Documentation matches the actual implementation.
- Docker and deployment configuration are verified.
- The application works at a real public URL.
- Known limitations are documented honestly.

---

## 19. Current Priorities

The immediate priorities are:

1. Inspect the repository and local development environment.
2. Verify Python, Java, Node.js, npm, Docker, and MySQL availability.
3. Confirm compatible PySpark and Java versions before Spark integration.
4. Establish the React + Vite and FastAPI foundation.
5. Add configuration and the health endpoint.
6. Add and execute initial tests.
7. Document the exact commands required to run both applications.

Do not implement all analytics, document processing, NLP, database history, and deployment in the first pass.

Do not create the entire application as one large generated code dump.

**Start with Phase 0 inspection and Phase 1 foundation only.**

After Phase 1 has been implemented, tested, and reported, stop and wait for approval before beginning Phase 2.

---

## 20. Initial Agent Task

Read `PROJECT_CONTEXT.md` completely and treat it as the primary project requirements document for Word Intelligence v0.4.

Begin with repository inspection and the Phase 1 foundation.

First, inspect existing files and available runtimes. Then create or update only the files necessary to establish the React + Vite frontend, FastAPI backend, configuration, health endpoint, and initial tests.

---

## 21. Additional Feature Proposal — Image Text Extraction and Analysis (OCR)

**Feature status:** Proposed — not yet implemented  
**Priority:** Medium  
**Implementation phase:** After core analytics and document extraction are stable  
**Feature category:** Image Processing, OCR, Text Analytics

### 21.1 Feature Overview

Word Intelligence should optionally support extracting text from images and analysing the extracted text using the existing analytics pipeline.

Users should be able to upload an image containing readable text. The application extracts the text using Optical Character Recognition (OCR) and processes the extracted content using the same analytics services used for raw text, PDFs, DOCX files, TXT files, and webpages.

Examples include:

- Photographs of printed documents.
- Screenshots containing text.
- Scanned pages saved as images.
- Posters, notices, and announcements.
- Text contained in simple infographics.
- Receipts and forms containing readable printed text.

The initial implementation should focus on printed text. Handwriting recognition, complex document-layout understanding, and specialized receipt or form extraction are outside the initial scope.

### 21.2 Recommended Technology

Use **Tesseract OCR through `pytesseract`** as the initial OCR solution.

Required components:

- `pytesseract` — Python wrapper for Tesseract OCR.
- Tesseract OCR engine — external executable that performs recognition.
- Pillow (`PIL`) — image loading and basic preprocessing.
- Existing FastAPI backend — receives and validates image uploads.
- Existing analysis services — analyse the extracted text.
- Existing React frontend — provides upload controls and displays results.

Tesseract must be installed in the development and deployment environments. Installing `pytesseract` alone does not install the OCR engine.

Before choosing final versions, verify compatibility with the project's Python runtime, operating system, and Docker image.

Do not introduce a paid OCR service or a large deep-learning model unless the initial OCR approach proves insufficient and the change is approved.

### 21.3 Supported Image Formats

The initial version may support:

- PNG
- JPG
- JPEG
- WEBP

Support must be verified against the installed image-processing and OCR dependencies.

The backend must not trust the filename extension or client-provided MIME type alone. Validate the actual file content and ensure the image can be decoded safely.

Set configurable limits for:

- Maximum upload size.
- Maximum image dimensions and total pixel count.
- OCR processing time.
- Extracted-text length.

Reject corrupted, unsupported, oversized, or suspicious files with controlled error responses.

### 21.4 Processing Workflow

The image-analysis workflow should be:

1. The user uploads an image through the React interface.
2. FastAPI validates the file type, size, and image dimensions.
3. The document service safely decodes the image.
4. Pillow optionally preprocesses the image to improve recognition.
5. Tesseract extracts text from the image.
6. The backend validates the OCR output and checks whether usable text was found.
7. The extracted text is passed to the existing analysis service.
8. The analytics engine calculates word statistics and other supported metrics.
9. The NLP service calculates sentiment and noun phrases where appropriate.
10. The API returns the extracted text and analytical results.
11. React displays the extracted text and analysis dashboard.

The OCR workflow must reuse existing analytics logic rather than creating a separate implementation of word counts, bigrams, or sentiment analysis.

### 21.5 OCR Preprocessing

Preprocessing may improve recognition for low-quality images.

Potential operations include:

- Converting images to grayscale.
- Resizing images within safe dimension limits.
- Applying thresholding when useful.
- Correcting image orientation when reliably detectable.
- Improving contrast.
- Applying limited noise reduction.

Do not apply every preprocessing operation blindly. Image preprocessing can sometimes reduce accuracy, so compare the results using representative test images.

The original image should remain unchanged unless a specific requirement justifies modifying or storing it.

### 21.6 API Design

Add a dedicated endpoint:

`POST /api/v1/analysis/image`

Use multipart form data to receive the uploaded image.

The endpoint should:

- Validate the uploaded image.
- Perform OCR.
- Reuse the common analysis pipeline.
- Return the extracted text and analytical results.
- Return controlled errors when OCR fails or no readable text is detected.

The response should follow the same analysis schema as other input sources, with additional OCR-specific metadata where useful.

Possible metadata includes:

- Source type: `image`.
- OCR engine.
- OCR language.
- Whether preprocessing was applied.
- A warning when recognition quality may be limited.

Do not return fabricated OCR confidence scores. Only include confidence information when it is actually available and meaningfully supported by the OCR engine.

### 21.7 Frontend Requirements

Add an image-upload option to the existing analysis interface.

The interface should provide:

- Image selection and upload.
- Supported-format information.
- File-size validation feedback.
- A preview of the selected image, where practical.
- A visible OCR-processing state.
- A section displaying the extracted text.
- The existing word-statistics dashboard.
- Existing charts, tables, and CSV export.
- Clear errors for unreadable images or failed OCR.

Users should be able to review the extracted text before analysing it again or copying it, if this can be implemented without unnecessarily complicating the initial workflow.

Do not build a separate dashboard exclusively for images. Image-derived text should use the same results interface as other supported inputs.

### 21.8 Error Handling

Handle at least the following cases:

- Unsupported image format.
- Corrupted image.
- Empty image or image containing no readable text.
- Excessive image dimensions.
- Oversized upload.
- OCR executable missing from the runtime.
- Required OCR language data missing.
- OCR timeout.
- Image preprocessing failure.
- Extracted text exceeding configured limits.

Return useful messages to the user without exposing internal filesystem paths, stack traces, or sensitive configuration.

If OCR dependencies are unavailable, report the configuration problem. Do not silently return empty or invented text.

### 21.9 Testing Requirements

Create automated tests for:

- Valid images containing known printed text.
- Empty or unreadable images.
- Unsupported file types.
- Corrupted image files.
- Oversized uploads.
- Image dimension limits.
- OCR engine unavailability.
- OCR timeout handling.
- Integration between OCR and the existing analysis service.
- Correct word counts and bigrams for extracted text.

Use small, controlled test images with known expected text. OCR results can vary with image quality, so design integration tests with appropriate tolerances and keep deterministic unit tests around validation and service behaviour.

Do not rely exclusively on manually uploading images through the browser.

### 21.10 Security and Privacy

- Validate image content instead of trusting filenames.
- Enforce upload and decompression limits.
- Process images using controlled temporary storage.
- Remove temporary files after processing.
- Do not execute uploaded content.
- Avoid permanently storing original images by default.
- Do not log extracted text unnecessarily.
- Keep image-processing dependencies updated.
- Apply request timeouts and appropriate concurrency limits.
- Ensure images cannot be used to exhaust available CPU or memory.

### 21.11 Performance Considerations

OCR is generally more computationally expensive than analysing already-extracted text.

The application should:

- Apply strict image-size limits.
- Avoid unnecessary repeated OCR on the same request.
- Measure processing time on representative images.
- Limit concurrent OCR work according to hosting resources.
- Avoid blocking the entire application with uncontrolled long-running operations.

If OCR processing later becomes a major bottleneck, consider a background job system as a separate architectural decision. Do not introduce a queue solely for the initial implementation.

### 21.12 Implementation Conditions

Implement image OCR only after the existing core analysis pipeline and document extraction functionality are verified.

The implementation must:

1. Reuse the existing service architecture.
2. Follow the established API and response conventions.
3. Include automated tests.
4. Document Tesseract installation and language-data requirements.
5. Update `requirements.txt` and the Docker configuration where necessary.
6. Verify OCR functionality in the actual deployment environment.
7. Update the README with supported image formats and known limitations.

### 21.13 Acceptance Criteria

The feature is considered complete when:

- Users can upload a supported image through the public website.
- The backend validates and safely processes the image.
- Readable printed text is extracted correctly for the verified test cases.
- Extracted text enters the existing analysis pipeline.
- Results are displayed in the existing dashboard.
- Invalid images and OCR failures produce controlled errors.
- Upload limits and temporary-file cleanup work.
- Automated tests pass.
- OCR works in the deployed environment, not only on the developer's computer.
- Documentation accurately describes supported formats and OCR limitations.

### 21.14 Scope Boundary

This feature provides OCR-based text extraction followed by ordinary text analytics. It does not guarantee perfect recognition and is not intended to authenticate images, detect image manipulation, interpret every visual element, or perform advanced document understanding.

Treat OCR output as potentially imperfect text. Users should be able to review it before relying on analytical results.

**Implementation instruction for the coding agent:** Do not implement this feature until its prerequisite phases are complete and explicit approval has been provided.
---

Do not implement the full application in one pass. Do not introduce unrelated infrastructure or additional dependencies without justification. Do not invent command outputs or test results.

Run the relevant verification commands and report:

1. What was found during inspection.
2. What was implemented.
3. Which files were created or modified.
4. Which commands were executed.
5. The actual results of those commands.
6. Any unresolved compatibility issues.
7. Exact local startup instructions.
8. What remains before Phase 1 can be considered complete.

**Stop after reporting Phase 1. Wait for explicit approval before proceeding.**
