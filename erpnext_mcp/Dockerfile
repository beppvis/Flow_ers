FROM python:3.11-slim

# Install system dependencies for PDF and OCR processing
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Install fpdf for sample generation if needed
RUN pip install fpdf

# Copy application code
COPY . .

# Expose the API port
EXPOSE 8000
# User was using 8001 recently, but standard is 8000. 
# We'll map 8001:8000 in compose or just use 8001 inside.
# Let's stick to 8000 inside and map it.

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
