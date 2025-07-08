# Firecrawl-Streamlit Web Scraper
# Multi-stage Docker build for development and production

# Base Python image with security updates
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -m appuser

# Set working directory
WORKDIR /app

# Copy requirements first (Docker layer caching optimization)
COPY requirements.txt .

# Install Python dependencies in virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Development stage
FROM base as development

# Install development dependencies
RUN pip install \
    pytest \
    pytest-cov \
    black \
    flake8 \
    mypy \
    jupyter \
    ipython

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app /opt/venv
USER appuser

# Create necessary directories
RUN mkdir -p /app/data/scraped_content \
    /app/data/processed_content \
    /app/data/metadata \
    /app/data/exports \
    /app/data/backups \
    /app/data/temp \
    /app/logs

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default command for development
CMD ["streamlit", "run", "streamlit-app/app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]

# Production stage
FROM base as production

# Copy only necessary files for production
COPY requirements.txt .
COPY streamlit-app/ ./streamlit-app/
COPY config/ ./config/
COPY .env.example .env.example

# Change ownership to non-root user
RUN chown -R appuser:appuser /app /opt/venv
USER appuser

# Create necessary directories
RUN mkdir -p /app/data/scraped_content \
    /app/data/processed_content \
    /app/data/metadata \
    /app/data/exports \
    /app/data/backups \
    /app/data/temp \
    /app/logs

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Production command with optimizations
CMD ["streamlit", "run", "streamlit-app/app.py", \
     "--server.address", "0.0.0.0", \
     "--server.port", "8501", \
     "--server.headless", "true", \
     "--server.enableCORS", "false", \
     "--server.enableXsrfProtection", "true"]
