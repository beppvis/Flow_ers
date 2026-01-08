# Automated Quote Processor

**Build2Break Hackathon - LogiTech Domain**

Automated quote processing system for logistics companies. Automates the entry of quotes from various formats (PDF, Images, Excel, Word, Text) into ERPNext, eliminating manual data entry.

## Problem Statement

Logistics coordinators spend hours daily manually re-typing quotes from forwarders into Excel sheets for comparison. Quotes arrive in inconsistent formats (PDF, Excel with merged cells, WhatsApp messages), making the process time-consuming and error-prone.

## Solution

This system automates quote processing by:
- Accepting quotes in multiple formats (PDF, Images, Excel, Word, Text)
- Extracting structured data using AI/OCR
- Validating and standardizing quote information
- Pushing data directly to ERPNext via API

## Tech Stack

- **Frontend**: React + Vite
- **Backend API**: Python + FastAPI
- **MCP Agent**: Python (Model Context Protocol)
- **Containerization**: Docker + Docker Compose
- **ERP Integration**: ERPNext API (to be implemented)

## Project Structure

```
.
├── client/          # React frontend application
├── backend/         # FastAPI backend service
├── mcp_agent/       # Python MCP agent for quote processing
├── docker-compose.yml
└── README.md
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Node.js 20+ (for local development)

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd quote-processor
```

2. Build and start services:
```bash
docker-compose up --build
```

3. Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

### Local Development

1. Install dependencies:
```bash
# Backend (Python)
cd backend && pip install -r requirements.txt

# Frontend (Node.js)
cd client && npm install
```

2. Start development servers:
```bash
# From root directory
npm run dev
```

This starts both frontend (port 5173) and backend (port 5000) concurrently.

## Features

### Current Implementation

- Multi-format file upload (PDF, Images, Excel, Word, Text)
- Drag-and-drop interface
- File validation (size, type, extension)
- Secure file handling
- Rate limiting
- Error handling and user feedback
- Responsive design
- Python FastAPI backend
- Dockerized microservices architecture

### To Be Implemented

- OCR/Data extraction from images and PDFs (MCP Agent)
- Excel parsing with merged cell handling (MCP Agent)
- WhatsApp message parsing (MCP Agent)
- ERPNext API integration (MCP Agent)
- Quote comparison dashboard
- Data validation and standardization (MCP Agent)

## API Endpoints

### `GET /api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

### `POST /api/upload`
Upload quote files.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `quotes` (array of files, max 5 files, 10MB each)

**Response:**
```json
{
  "success": true,
  "message": "Successfully uploaded 2 file(s)",
  "files": [
    {
      "id": "1234567890-filename.pdf",
      "originalName": "quote.pdf",
      "size": 1024000,
      "mimetype": "application/pdf",
      "uploadedAt": "2024-01-01T00:00:00.000Z"
    }
  ]
}
```

## Security Features

- File type validation (MIME type + extension)
- File size limits (10MB per file)
- Rate limiting (50 requests per 15 minutes)
- Filename sanitization
- CORS protection
- Security headers (FastAPI middleware)
- Input validation

## Build2Break Considerations

### Architecture
- Microservices architecture (frontend + backend)
- Dockerized for easy deployment
- Clear separation of concerns

### Robustness
- Comprehensive error handling
- Input validation at multiple layers
- Rate limiting to prevent abuse
- File validation (type, size, content)

### Security
- Secure file upload handling
- Input sanitization
- CORS configuration
- Security headers

## Domain Alignment (LogiTech)

This solution addresses:
- **Operational Efficiency**: Automates manual quote entry
- **Visibility**: Centralized quote management
- **Supply Chain Coordination**: Streamlines vendor quote comparison

## Assumptions & Limitations

### Assumptions
- ERPNext is accessible via API
- Quotes follow common formats (not completely unstructured)
- Users have basic technical knowledge

### Limitations
- OCR accuracy depends on image quality
- Complex Excel formats may require manual review
- WhatsApp message parsing requires specific format
- Maximum 5 files per upload
- 10MB file size limit per file

## Development

### Running Tests
```bash
# Backend tests (to be implemented)
cd backend && pytest

# Frontend tests (to be implemented)
cd client && npm test
```

### Building for Production
```bash
# Using Docker (recommended)
docker-compose up --build

# Or manually:
# Build frontend
cd client && npm run build

# Start backend
cd backend && uvicorn main:app --host 0.0.0.0 --port 5000
```

## Contributing

This is a hackathon project. For Build2Break, ensure:
- All code is properly documented
- Docker setup works out of the box
- README includes setup instructions
- Code follows security best practices

## License

MIT License - Build2Break Hackathon Project

## Team

- UI/UX: [Your Name]
- Backend: [Team Member]
- Full Stack: [Team Member]

---

**Build2Break Hackathon 2024 - LogiTech Domain**

