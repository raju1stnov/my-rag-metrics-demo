# Use the official Python 3.9 image
FROM python:3.9-slim

WORKDIR /app

# Copy all service files
COPY . /app

# Install dependencies
RUN pip install fastapi uvicorn prometheus_client

# Default command (can be overridden by docker-compose.yml)
CMD ["uvicorn", "vectorlens_service:app", "--host", "0.0.0.0", "--port", "8000"]