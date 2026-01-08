# Setup Instructions - Quote Processor

## Quick Start with Docker (Recommended)

### Prerequisites
- Docker Desktop installed and running
- Docker Compose v3.8+

### Steps

1. **Clone/Navigate to project directory**
   ```bash
   cd quote-processor
   ```

2. **Build and start all services**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend UI: http://localhost:5173
   - Backend API: http://localhost:5000
   - Health Check: http://localhost:5000/api/health

4. **Stop services**
   ```bash
   docker-compose down
   ```

## Local Development Setup

### Prerequisites
- Node.js 20+ installed
- npm or yarn

### Steps

1. **Install root dependencies (for dev scripts)**
   ```bash
   npm install
   ```

2. **Install backend dependencies (Python)**
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

3. **Install frontend dependencies**
   ```bash
   cd client
   npm install
   cd ..
   ```

4. **Start development servers**
   ```bash
   # From root directory - starts both frontend and backend
   npm run dev
   ```

   Or start them separately:
   ```bash
   # Terminal 1 - Backend (Python FastAPI)
   cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 5000

   # Terminal 2 - Frontend (React)
   cd client && npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:5173
   - Backend: http://localhost:5000

## Testing the Upload

1. Open http://localhost:5173 in your browser
2. Click or drag and drop a file (PDF, Image, Excel, Word, or Text)
3. Files will be validated and uploaded to the backend
4. Check `server/uploads/` directory for uploaded files

## Troubleshooting

### Port Already in Use
If port 5000 or 5173 is already in use:
- Change ports in `docker-compose.yml` or
- Stop the service using those ports

### Docker Build Fails
- Ensure Docker Desktop is running
- Check Docker has enough resources allocated
- Try: `docker-compose down -v` then rebuild

### File Upload Fails
- Check backend is running: http://localhost:5000/api/health
- Check browser console for errors
- Verify file size is under 10MB
- Verify file type is supported

### CORS Errors
- Ensure `ALLOWED_ORIGINS` in backend environment matches frontend URL
- Check backend CORS configuration in `backend/main.py`

## Project Structure

```
quote-processor/
├── client/              # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   └── App.jsx      # Main app component
│   ├── Dockerfile
│   └── package.json
├── backend/             # Python FastAPI backend
│   ├── uploads/         # Uploaded files directory
│   ├── main.py          # Main API server
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile
├── mcp_agent/           # Python MCP agent
│   ├── main.py          # MCP agent implementation
│   ├── requirements.txt # MCP dependencies
│   └── Dockerfile
├── docker-compose.yml   # Docker orchestration
└── README.md
```

## Next Steps

1. Test file upload functionality
2. Implement MCP agent in `mcp_agent/main.py`:
   - OCR/data extraction from images and PDFs
   - Excel parsing with merged cell handling
   - WhatsApp message parsing
   - ERPNext API integration
3. Add quote comparison dashboard
4. Implement data validation and standardization

## Build2Break Submission Checklist

- [x] Docker Compose file working
- [x] All services containerized
- [x] Setup instructions documented
- [x] GitHub repository ready
- [x] Project description complete
- [ ] Data extraction implemented
- [ ] ERPNext integration complete
- [ ] System tested end-to-end

