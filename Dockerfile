FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
COPY requirements-dev.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p logs data config && \
    chmod 755 logs data config

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create non-root user for security
RUN useradd -m -u 1000 trader && \
    chown -R trader:trader /app
USER trader

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command
CMD ["python", "trader_daemon.py"]
