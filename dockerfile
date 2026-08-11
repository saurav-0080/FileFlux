# Use official lightweight Python image
# slim variant removes unnecessary system packages — smaller image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Set environment variables
# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout/stderr — logs appear immediately
ENV PYTHONUNBUFFERED=1
# Default log level — can be overridden at runtime
ENV LOG_LEVEL=INFO
# Default database path — points to mounted volume
ENV DATABASE_PATH=/app/database/organizer.db

# Copy requirements first (Docker caches this layer)
# If requirements don't change, Docker skips reinstalling on rebuild
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app/ ./app/
COPY main.py .
COPY config/ ./config/

# Create required directories inside the container
RUN mkdir -p /app/database /app/reports /app/logs

# Mount points for persistent data
# /data = user files to organize
# /app/database = SQLite database persistence
VOLUME ["/data", "/app/database"]

# Default command — show help if no command given
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]