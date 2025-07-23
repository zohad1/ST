# Dockerfile - Fixed for Backend Services with improved network handling

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
# Add pip configuration for better network handling
ENV PIP_DEFAULT_TIMEOUT=120
ENV PIP_RETRIES=5
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies including network tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        libpq-dev \
        curl \
        build-essential \
        gcc \
        libssl-dev \
        libffi-dev \
        ca-certificates \
        netcat-openbsd \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create pip configuration for better package resolution
RUN mkdir -p /root/.pip && \
    echo "[global]" > /root/.pip/pip.conf && \
    echo "timeout = 120" >> /root/.pip/pip.conf && \
    echo "retries = 5" >> /root/.pip/pip.conf && \
    echo "trusted-host = pypi.org pypi.python.org files.pythonhosted.org" >> /root/.pip/pip.conf

# Upgrade pip, setuptools, and wheel to latest versions
RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with fallback options
RUN pip install --no-cache-dir -r requirements.txt || \
    (echo "Retrying with --use-deprecated=legacy-resolver..." && \
     pip install --no-cache-dir --use-deprecated=legacy-resolver -r requirements.txt) || \
    (echo "Installing packages individually..." && \
     pip install --no-cache-dir fastapi==0.104.1 && \
     pip install --no-cache-dir uvicorn[standard]==0.24.0 && \
     pip install --no-cache-dir python-multipart==0.0.6 && \
     pip install --no-cache-dir SQLAlchemy>=2.0.0,<2.1.0 && \
     pip install --no-cache-dir -r requirements.txt --no-deps)

# Copy application code
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${SERVICE_PORT:-8002}/health || exit 1

# Expose port (will be overridden by docker-compose)
EXPOSE ${SERVICE_PORT:-8002}

# Default command (will be overridden by docker-compose for development)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]