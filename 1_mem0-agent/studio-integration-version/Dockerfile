# Sử dụng multi-stage build
FROM python:3.10-slim AS builder

WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY ./studio-integration-version/requirements.txt .

# Install only build dependencies and create a virtual environment
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH" \
    PORT=8001

WORKDIR /app

# Cài đặt thư viện hệ thống cần thiết
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder stage
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY ./studio-integration-version/*.py .
COPY ./studio-integration-version/.env* ./

# Expose the port
EXPOSE ${PORT}

# Set the command to run the application
CMD ["sh", "-c", "uvicorn mem0_agent_endpoint:app --host 0.0.0.0 --port ${PORT} --workers 4"]
