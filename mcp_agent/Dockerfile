FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed for OCR/processing
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (if MCP agent runs as a service)
# EXPOSE 8000

# Run MCP agent
CMD ["python", "main.py"]

