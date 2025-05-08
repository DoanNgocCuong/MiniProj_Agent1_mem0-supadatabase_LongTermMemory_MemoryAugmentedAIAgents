FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages directly
RUN pip install --no-cache-dir \
    streamlit \
    openai \
    python-dotenv \
    supabase \
    numpy==1.26.4 \
    mem0ai==0.1.65 \
    vecs \
    psycopg2-binary

# Copy application code, .env file, and avatar image
COPY ./iterations/v3-streamlit-supabase-mem0.py .
COPY ./iterations/.env .env
COPY ./iterations/baby.png .

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "v3-streamlit-supabase-mem0.py", "--server.port=8501", "--server.address=0.0.0.0"]
