# Architecture Documentation

## System Architecture

This system follows a microservices architecture with clear separation of concerns:

```
┌─────────────┐
│   Client    │  React Frontend (Port 5173)
│  (Browser)  │
└──────┬──────┘
       │ HTTP/REST
       │
┌──────▼──────────┐
│  Backend API    │  FastAPI Service (Port 5000)
│  (FastAPI)      │  - File upload handling
│                 │  - Validation & security
│                 │  - Rate limiting
└──────┬──────────┘
       │
       │ File storage
       │
┌──────▼──────────┐
│  MCP Agent      │  Python MCP Service
│  (Python)       │  - OCR/Data extraction
│                 │  - Quote processing
│                 │  - ERPNext integration
└─────────────────┘
```

## Service Breakdown

### 1. Frontend Service (React + Vite)
- **Technology**: React 18, Vite
- **Purpose**: User interface for quote upload
- **Responsibilities**:
  - File upload UI with drag-and-drop
  - Client-side validation
  - User feedback and error handling
  - Responsive design

### 2. Backend API Service (FastAPI)
- **Technology**: Python 3.11, FastAPI, Uvicorn
- **Purpose**: RESTful API for file handling
- **Responsibilities**:
  - File upload endpoint
  - File validation (type, size, extension)
  - Security (rate limiting, CORS, input sanitization)
  - File storage management
  - Health checks

### 3. MCP Agent Service (Python)
- **Technology**: Python 3.11, MCP SDK
- **Purpose**: Quote processing and ERPNext integration
- **Responsibilities**:
  - OCR for images/PDFs
  - Excel parsing (including merged cells)
  - Data extraction and validation
  - ERPNext API integration
  - Quote standardization

## Why This Architecture is Robust

### 1. Separation of Concerns
- Each service has a single, well-defined responsibility
- Changes to one service don't affect others
- Easy to test and maintain

### 2. Technology Choices

**FastAPI over Node.js/Express:**
- Better performance for async operations
- Built-in data validation with Pydantic
- Automatic API documentation
- Type safety with Python
- Better error handling

**Python for MCP Agent:**
- Rich ecosystem for OCR (Tesseract, EasyOCR)
- Excellent libraries for Excel parsing (openpyxl, pandas)
- Strong AI/ML integration capabilities
- Better suited for data processing tasks

**React Frontend:**
- Modern, performant UI framework
- Strong ecosystem
- Easy to secure and validate inputs
- Responsive design capabilities

### 3. Security Hardening

**Multiple Validation Layers:**
- Client-side validation (immediate feedback)
- Backend validation (MIME type, extension, size)
- File content validation (future: magic bytes)

**Rate Limiting:**
- Prevents abuse and DoS attacks
- Configurable limits per endpoint
- IP-based tracking

**Input Sanitization:**
- Filename sanitization (path traversal prevention)
- File size limits (prevents resource exhaustion)
- Type whitelisting (prevents malicious uploads)

**Network Security:**
- CORS configuration
- Security headers
- Docker network isolation

### 4. Dockerization Benefits

**Reproducibility:**
- Same environment across all deployments
- No "works on my machine" issues
- Easy to test and validate

**Isolation:**
- Services run in separate containers
- Network isolation between services
- Resource limits per container

**Scalability:**
- Easy to scale individual services
- Can add more MCP agent instances if needed
- Load balancing ready

### 5. Error Handling

**Graceful Degradation:**
- Services continue operating if one fails
- Health checks for monitoring
- Clear error messages for debugging

**Comprehensive Logging:**
- Structured logging ready
- Error tracking capabilities
- Audit trail for security

## Build2Break Considerations

### Attack Surface Reduction
- Minimal exposed endpoints
- Strict input validation
- No unnecessary services running
- Network isolation

### Defensive Programming
- Multiple validation layers
- Fail-safe defaults
- Resource limits
- Timeout handling

### Observability
- Health check endpoints
- Structured error responses
- Logging infrastructure ready

### Maintainability
- Clear code structure
- Well-documented APIs
- Type hints in Python
- Consistent error handling

## Potential Vulnerabilities to Address

1. **File Upload Attacks**
   - Mitigated by: Type validation, size limits, filename sanitization
   - Future: Magic byte validation, virus scanning

2. **Rate Limiting Bypass**
   - Mitigated by: IP-based limiting, multiple rate limiters
   - Future: User authentication, token-based limiting

3. **Path Traversal**
   - Mitigated by: Filename sanitization, restricted upload directory
   - Future: Chroot jail, sandboxing

4. **DoS via Large Files**
   - Mitigated by: File size limits, chunked processing
   - Future: Async processing queue

5. **CORS Misconfiguration**
   - Mitigated by: Environment-based CORS, strict origins
   - Future: Preflight request validation

## Future Enhancements

1. **Authentication & Authorization**
   - JWT tokens
   - Role-based access control
   - API key management

2. **Queue System**
   - Async job processing
   - Retry mechanisms
   - Job status tracking

3. **Monitoring**
   - Prometheus metrics
   - Grafana dashboards
   - Alerting

4. **Testing**
   - Unit tests
   - Integration tests
   - Security testing (OWASP)

## Communication Flow

1. User uploads file via frontend
2. Frontend validates file (client-side)
3. Frontend sends file to Backend API
4. Backend API validates file (server-side)
5. Backend API stores file
6. Backend API triggers MCP Agent (future: via queue)
7. MCP Agent processes file
8. MCP Agent extracts data
9. MCP Agent sends to ERPNext
10. Response flows back to user

This architecture provides a solid foundation that is both secure and maintainable, suitable for the Build2Break hackathon's adversarial testing environment.

