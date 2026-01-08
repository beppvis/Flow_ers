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


@app.post("/parse")
async def parse_files(quotes: List[UploadFile] = File(...)):
    """
    Parses uploaded files and returns stringified JSON data of items.
    Does NOT insert into ERPNext.
    """
    processed_results = []

    # Use one processor instance
    processor = FileProcessor()

    for file in quotes:
        try:
            content = await file.read()
            items = processor.process_file(content, file.filename)

            processed_results.extend(items)

        except ValueError as ve:
            # Explicit validation error
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            # We might want to return errors in a way the frontend can display,
            # but for now let's just log it or include a placeholder error item if needed.
            print(f"Error processing {file.filename}: {e}")
            raise HTTPException(status_code=500, detail=f"Error processing {file.filename}: {e}")

    return {
        "success": True,
        "message": f"Successfully parsed {len(quotes)} files.",
        "data": processed_results
    }


@app.post("/insert")
async def insert_items(items: List[dict]):
    """
    Receives a list of item dictionaries and inserts them into ERPNext.
    """
    client = get_erp_client()
    if not client:
        raise HTTPException(
            status_code=500, detail="ERPNext client not initialized")

    results = []
    for item in items:
        try:
            res = client.create_item(item)
            results.append({
                "item_code": item.get("item_code"),
                "status": "success" if res and res.get("name") else "failed",
                "message": res.get("message", "Item created successfully") if res and res.get("name") else res.get("exception", "Unknown error during creation")
            })
        except Exception as e:
            results.append({
                "item_code": item.get("item_code"),
                "status": "failed",
                "message": str(e)
            })

    return {
        "success": True,
        "message": "Insertion complete",
        "results": results
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
