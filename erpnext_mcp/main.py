from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from processor import FileProcessor
from erpnext_client import ERPNextClient
import uvicorn
import os

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ERPNext MCP Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = FileProcessor()
# Lazy initialization to allow starting even if env vars are missing (will fail on usage)
erp_client = None


def get_erp_client():
    global erp_client
    if erp_client is None:
        try:
            erp_client = ERPNextClient()
        except Exception as e:
            print(f"Warning: ERPNext client failed to initialize: {e}")
            return None
    return erp_client


@app.post("/upload")
async def upload_file(quotes: List[UploadFile] = File(...)):
    """
    Upload PDF or Excel files.
    The client sends files with the key 'quotes'.
    """
    processed_results = []

    try:
        client = get_erp_client()

        for file in quotes:
            try:
                content = await file.read()
                items = processor.process_file(content, file.filename)

                # Check for client availability for each file or once globally
                if client:
                    for item in items:
                        print(item)
                        if item["item_code"]:
                            res = client.create_item(item)
                            print(res)
                            processed_results.append({
                                "filename": file.filename,
                                "item": item.get("item_code"),
                                "status": "success",
                                "erp_response": res
                            })
                        else:
                            processed_results.append({
                                "filename": file.filename,
                                "item": "unknown",
                                "status": "skipped"
                            })
                else:
                    processed_results.append({
                        "filename": file.filename,
                        "status": "processed_locally_only",
                        "items_count": len(items)
                    })
            except Exception as e:
                print(f"Error processing {file.filename}: {e}")
                processed_results.append(
                    {"filename": file.filename, "error": str(e)})

        # Return format expected by QuoteUploader.jsx: { success: true, message: "..." }
        return {
            "success": True,
            "message": f"Successfully processed {len(quotes)} files.",
            "details": processed_results
        }

    except Exception as e:
        print(f"Upload error: {e}")
        # Return 500 but try to keep structure if possible, though FastAPI exception handler takes over
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
