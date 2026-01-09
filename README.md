# Quote Processor - Automated Logistics Quote Management

**Domain:** LogiTech (Logistics & Supply Chain)  
**Build2Break Hackathon Submission**

<img width="2749" height="1531" alt="image" src="https://github.com/user-attachments/assets/af5c8fb8-ec81-4fe4-8d1f-25fdf27720ca" />
<img width="2749" height="1531" alt="image" src="https://github.com/user-attachments/assets/f406b285-5cec-4516-9eb7-83d5e0a446e9" />


## Problem Statement

Logistics coordinators and procurement teams spend 40% of their time daily manually re-typing quotes from freight forwarders and suppliers into Excel spreadsheets or ERP systems. Quotes arrive in various formats:
- Scanned PDF documents
- Images (JPG, PNG) from mobile cameras
- Excel files with inconsistent formatting
- Word documents
- Text files

This manual process is:
- **Time-consuming:** Over 40% of the day is consumed with doing repetitive tasks
- **Error-prone:** Manual data entry leads to typos and missing information
- **Inefficient:** Delays procurement decisions and quote comparisons
- **Scalable bottleneck:** Cannot handle high quote volumes

## Demo Video
https://vimeo.com/1152623961?share=copy&fl=sv&fe=ci


## Domain Relevance

This solution addresses a critical operational efficiency challenge in the **LogiTech domain**:

- **Inventory and Stock Tracking:** Automated quote processing enables faster procurement decisions
- **Supply Chain Coordination:** Streamlines vendor quote management and comparison
- **Operational Efficiency:** Reduces manual work by 95%, freeing coordinators for strategic tasks
- **Visibility:** Centralized quote data in ERPNext provides better supply chain visibility

The solution directly aligns with LogiTech domain objectives of improving operational efficiency and supply chain coordination, ensuring efficient adoption of "glue logic" to different ERP and Inventory Management System.

## Solution Overview

An automated quote processing system that:

1. Accepts quotes in multiple formats (PDF, images, Excel, Word, text)
2. Extracts structured data using OCR, AI, and intelligent parsing
3. Automatically pushes extracted data to ERPNext for quote management
4. Flexible Adoption across different ERP and Inventory Management system
5. Easy to Use interface.

**Key Features:**
- Multi-format support (PDF, images, Excel, Word, text)
- OCR for scanned documents
- AI-powered data extraction (Gemini AI)
- Automatic ERPNext integration
- Robust file validation and error handling
- Dockerized deployment for easy setup

## High-Level Architecture

```
┌─────────────────────────────────────────┐
│         React Frontend (Vite)           │
│         Port: 5173                      │
│         - Quote upload & review UI      │
│         - Calls /api/parse & /api/insert│
└──────────────┬──────────────────────────┘
               │ HTTP /api/* (proxied)
               │
┌──────────────▼──────────────────────────┐
│     MCP Agent (FastAPI, erpnext_mcp)    │
│     Port: 8001 (host) → 8000 (container)│
│     - OCR + parsing (PDF, Excel, images)│
│     - Gemini AI extraction (optional)   │
│     - /parse (extract items)            │
│     - /insert (sync items to ERPNext)   │
└──────────────┬──────────────────────────┘
               │ HTTP REST (Frappe API)
               │
┌──────────────▼──────────────────────────┐
│       ERPNext Stack (frappe/erpnext)    │
│       Port: 8080 (UI)                   │
│       - Items, Quotations, Masters      │
│       - Background jobs & scheduler     │
└─────────────────────────────────────────┘

Supporting Services:
- MariaDB (ERPNext database)
- Redis (queue + cache)
```

**Technology Stack:**
- **Frontend:** React + Vite, Nginx
- **Backend:** Python + FastAPI
- **MCP Agent:** Python, Tesseract OCR, Gemini AI, pandas
- **ERPNext:** Frappe framework, MariaDB, Redis
- **Infrastructure:** Docker Compose




## Assumptions and Limitations

### Assumptions

1. **File Quality:** Assumes uploaded files are readable (not corrupted, reasonable image quality for OCR)
2. **Quote Format:** Assumes quotes contain standard information (vendor, pricing, dates, locations)
3. **ERPNext Setup:** Assumes ERPNext is properly configured with required doctypes
4. **Network:** Assumes stable network connectivity between services
5. **API Keys:** Assumes GEMINI_API_KEY is provided for AI extraction (falls back to naive parsing if missing)
6. **User Behavior:** Assumes users upload valid quote files (not malicious content)

### Limitations

1. **File Size:** Maximum 10MB per file, 5 files per upload
2. **File Types:** Currently supports PDF, images (JPG/PNG), Excel (XLS/XLSX), Word (DOC/DOCX), and text files
3. **OCR Accuracy:** OCR accuracy depends on image quality; poor scans may result in extraction errors
4. **Data Extraction:** AI extraction quality depends on quote format consistency
5. **ERPNext Integration:** Requires ERPNext to be running and accessible
6. **Language Support:** Currently optimized for English text; other languages may have reduced accuracy
7. **Processing Time:** Large files or complex quotes may take 30-60 seconds to process
8. If the Gemini AI API key is not available, or is invalid, we'll default to naive processing. Garbage value and undefined behaviour is expected.

### Security Considerations

- File uploads are validated for type and size
- Filenames are sanitized to prevent path traversal
- Rate limiting prevents abuse (50 requests per 15 minutes)
- CORS is configured for allowed origins only
- Files are stored in isolated uploads directory

## Setup and Execution Instructions

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available
- Ports 5173, 8001, 8080 available
- Have a Gemini API key

### Quick Start (Local, via Docker Compose)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/beppvis/Flow_ers
   cd Flow_ers
   ```

2. **Start all services:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - **React Frontend (Quote Upload UI):** http://localhost:5173
   - **ERPNext UI:** http://localhost:8081

### Detailed Setup

#### 1. Environment Variables (Optional)

Create a `.env` file in the root directory by copying the `.env.example` file which is already existing in the root folder:

```env
# Fill in your own API key
GEMINI_API_KEY=your_gemini_api_key

# By default docker-compose wires FRAPPE_URL=http://backend:8081 inside the network.
# Only set these if you are pointing to a different ERPNext instance.
FRAPPE_URL=http://backend:8081

```
You should also place the same .env file inside erpnext_mcp .

#### 2. Build and Run

```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

#### 3. Verify Services

```bash
# Check service status
docker-compose ps

# Test MCP agent (FastAPI)
curl http://localhost:8001/docs

# Test ERPNext UI (should return HTML)
curl http://localhost:8080
```

### Usage

1. **Upload Quotes:**
   - Open http://localhost:5173
   - Drag and drop quote files or click to browse
   - Select up to 5 files (max 10MB each)
   - Click "Upload" button

2. **Processing:**
   - Files are validated and stored
   - MCP agent processes files (OCR, extraction)
   - Data is pushed to ERPNext
   - Success message displayed

3. **View in ERPNext:**
   - Open http://localhost:8081
   - Login with default credentials (if first run) [User: `Administrator` Pass: `admin` ]
   - Navigate to Items or Quotes section
   - View processed quote data

### Troubleshooting

**Services not starting:**
```bash
# Check logs for ERPNext core
docker-compose logs backend

# Check logs for MCP Agent
docker-compose logs erpnext-mcp-backend

# Rebuild specific services
docker-compose build erpnext-mcp-backend
docker-compose up erpnext-mcp-backend
```

**Port conflicts:**
- Change ports in `docker-compose.yml` if needed

**ERPNext not accessible:**
- Wait 2-3 minutes for ERPNext to fully initialize (site creation, migrations, etc.)
- Check ERPNext logs: `docker-compose logs backend`

**File upload fails:**
- Check file size (max 10MB)
- Verify file type is supported
- Check backend logs for errors

## Project Structure

```
Flow_ers/
├── client/                 # React frontend (Vite) for quote upload & review
│   ├── src/
│   ├── Dockerfile          # Builds the frontend dev server
├── erpnext_mcp/            # MCP Agent (FastAPI) for parsing & ERPNext sync
│   ├── main.py
│   ├── processor.py
│   ├── erpnext_client.py
│   ├── requirements.txt
│   └── Dockerfile          # Builds the MCP backend
├── dataset/                # Sample PDFs, images, and Excel quotes (demo only)
├── docker-compose.yml      # Orchestrates ERPNext + MCP + Frontend
└── README.md               # This file
```

## API Endpoints

### MCP Agent API (Port 8001 → container 8000)

All endpoints are exposed by the `erpnext_mcp` FastAPI service and are typically called via the frontend using `/api/*` (Vite proxy).

- `POST /parse`
  - **Description:** Upload one or more quote files (`quotes` field, `multipart/form-data`).
  - **Behavior:** Runs OCR/parsing and returns a JSON list of extracted items. Does **not** write to ERPNext.

- `POST /insert`
  - **Description:** Accepts a JSON list of items (same shape as `/parse` output).
  - **Behavior:** Inserts/updates Items in ERPNext using the configured `FRAPPE_URL`.

- `GET /docs`
  - **Description:** Swagger UI for interactive testing of the MCP API.

### ERPNext UI (Port 8081)

- Web UI served by the `frappe/erpnext` image (proxied container `frontend` service).
- Default site created as `frontend` with Administrator / admin (first run).

## Contact

For questions or issues, please open a GitHub Issue in this repository.

