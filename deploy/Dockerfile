# Multi-stage Dockerfile for ML Project deployment
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash mluser

WORKDIR /app

# Development stage
FROM base as development

# Copy requirements files
COPY requirements*.txt ./
COPY automl/requirements.txt ./automl-requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r automl-requirements.txt

# Copy source code
COPY . .

# Change ownership to mluser
RUN chown -R mluser:mluser /app

USER mluser

# Expose port
EXPOSE 8000

# Development command
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production

# Copy requirements files
COPY requirements*.txt ./
COPY automl/requirements.txt ./automl-requirements.txt

# Install Python dependencies (production only)
RUN pip install --upgrade pip && \
    pip install --no-dev -r requirements.txt && \
    pip install --no-dev -r automl-requirements.txt

# Copy only necessary files for production
COPY backend/ ./backend/
COPY automl/ ./automl/
COPY examples/ ./examples/
COPY docs/ ./docs/

# Create necessary directories
RUN mkdir -p /app/automl_results /app/mlruns /app/simple_tracking

# Change ownership to mluser
RUN chown -R mluser:mluser /app

USER mluser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Production command
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]