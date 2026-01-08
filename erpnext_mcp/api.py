from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from core_logic import core_process_file
import os
import shutil

app = FastAPI(title="ERPNext Integration API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file (PDF or Excel) to be processed and inserted into ERPNext.
    """
    if not file.filename:
         raise HTTPException(status_code=400, detail="No filename provided")

    # Create temp directory if not exists
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    
    file_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Process file using the shared core logic
        result = core_process_file(os.path.abspath(file_path))
        
        return {"filename": file.filename, "report": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
