# Word Intelligence v0.4 - Backend Production Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies: JRE for Apache PySpark, Tesseract OCR for image text extraction, curl, procps
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jre-headless \
    tesseract-ocr \
    tesseract-ocr-eng \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set Java environment for PySpark
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download required NLTK corpora for offline container execution
RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True); nltk.download('averaged_perceptron_tagger_eng', quiet=True); nltk.download('brown', quiet=True)"

# Copy application source and configuration
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]
