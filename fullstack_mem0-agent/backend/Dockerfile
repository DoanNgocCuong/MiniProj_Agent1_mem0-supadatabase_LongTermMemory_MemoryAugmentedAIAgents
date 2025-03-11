FROM python:3.10-slim

WORKDIR /app

# Cài đặt curl cho healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api.py .

# Expose API port
EXPOSE 8000

# Start API server
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"] 