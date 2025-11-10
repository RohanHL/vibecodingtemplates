# Dockerfile Template for FastAPI Application
# Use with Railway or other container platforms

# =============================================================================
# BASE IMAGE
# =============================================================================
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# =============================================================================
# DEPENDENCIES
# =============================================================================
FROM base as dependencies

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# =============================================================================
# APPLICATION
# =============================================================================
FROM dependencies as application

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# =============================================================================
# RUNTIME
# =============================================================================
# Expose port (Railway will set PORT environment variable)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Start application
# Railway provides PORT environment variable, default to 8000 if not set
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]

# =============================================================================
# ALTERNATIVE: With Database Migrations
# =============================================================================
# Uncomment below to run migrations before starting the app

# CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]

# =============================================================================
# ALTERNATIVE: With Gunicorn (for production)
# =============================================================================
# Uncomment below to use Gunicorn with multiple workers

# RUN pip install gunicorn
# CMD ["sh", "-c", "gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000}"]

# =============================================================================
# NOTES
# =============================================================================
# 1. Build: docker build -t myapp .
# 2. Run: docker run -p 8000:8000 myapp
# 3. Railway automatically uses PORT environment variable
# 4. For multi-stage builds, use "FROM dependencies as test" for testing
# 5. Keep image size small by using slim base and cleaning up after apt-get
