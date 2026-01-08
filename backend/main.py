"""
Quote Processor Backend API - FastAPI Implementation
Build2Break Hackathon - LogiTech Domain
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
import aiofiles

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILES = 5
ALLOWED_MIME_TYPES = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/jpg',
    'text/plain',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]
ALLOWED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.txt', '.xls', '.xlsx', '.doc', '.docx']

# Initialize FastAPI
app = FastAPI(
    title="Quote Processor API",
    description="Automated quote processing API for logistics",
    version="1.0.0"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# Response models
class FileInfo(BaseModel):
    id: str
    originalName: str
    size: int
    mimetype: str
    uploadedAt: str


class UploadResponse(BaseModel):
    success: bool
    message: str
    files: List[FileInfo]


class HealthResponse(BaseModel):
    status: str
    timestamp: str


# Utility functions
def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and injection attacks"""
    # Remove path components
    filename = os.path.basename(filename)
    # Remove dangerous characters
    filename = "".join(c for c in filename if c.isalnum() or c in ".-_")
    # Limit length
    filename = filename[:255]
    return filename


def validate_file(file: UploadFile) -> tuple[bool, Optional[str]]:
    """Validate file type and size"""
    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        return False, f"Invalid file type: {file.content_type}"
    
    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file extension: {ext}"
    
    return True, None


async def save_file(file: UploadFile) -> tuple[str, int]:
    """Save uploaded file and return filename and size"""
    # Validate file
    is_valid, error = validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = f"{timestamp}-{os.urandom(4).hex()}"
    sanitized_name = sanitize_filename(file.filename)
    filename = f"{unique_id}-{sanitized_name}"
    filepath = UPLOAD_DIR / filename
    
    # Read and save file with size check
    total_size = 0
    async with aiofiles.open(filepath, 'wb') as f:
        while chunk := await file.read(8192):  # 8KB chunks
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                # Clean up partial file
                if filepath.exists():
                    filepath.unlink()
                raise HTTPException(
                    status_code=413,
                    detail=f"File size exceeds {MAX_FILE_SIZE / (1024*1024)}MB limit"
                )
            await f.write(chunk)
    
    return filename, total_size


# API Endpoints
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@app.post("/api/upload", response_model=UploadResponse)
@limiter.limit("50/15minutes")
async def upload_files(
    request: Request,
    files: List[UploadFile] = File(...)
):
    """
    Upload quote files
    
    - Maximum 5 files per request
    - Maximum 10MB per file
    - Allowed types: PDF, Images, Excel, Word, Text
    """
    # Validate file count
    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_FILES} files allowed per request"
        )
    
    if len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="No files provided"
        )
    
    uploaded_files = []
    errors = []
    
    try:
        for file in files:
            try:
                filename, file_size = await save_file(file)
                
                uploaded_files.append(FileInfo(
                    id=filename,
                    originalName=file.filename,
                    size=file_size,
                    mimetype=file.content_type or "application/octet-stream",
                    uploadedAt=datetime.utcnow().isoformat() + "Z"
                ))
            except HTTPException as e:
                errors.append(f"{file.filename}: {e.detail}")
            except Exception as e:
                errors.append(f"{file.filename}: {str(e)}")
        
        if errors and not uploaded_files:
            # All files failed
            raise HTTPException(
                status_code=400,
                detail="; ".join(errors)
            )
        
        message = f"Successfully uploaded {len(uploaded_files)} file(s)"
        if errors:
            message += f". Errors: {'; '.join(errors)}"
        
        return UploadResponse(
            success=True,
            message=message,
            files=uploaded_files
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.exception_handler(413)
async def file_too_large_handler(request: Request, exc: HTTPException):
    """Handle file size limit exceeded"""
    return JSONResponse(
        status_code=413,
        content={"success": False, "error": "File size exceeds 10MB limit"}
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded"""
    return JSONResponse(
        status_code=429,
        content={"success": False, "error": "Too many requests. Please try again later."}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        reload=os.getenv("ENV") == "development"
    )

