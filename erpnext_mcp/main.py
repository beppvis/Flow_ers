from fastapi import FastAPI, UploadFile, File, HTTPException
from processor import FileProcessor
from erpnext_client import ERPNextClient
import uvicorn
import os

app = FastAPI(title="ERPNext MCP Server")

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
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a PDF or Excel file.
    The file is processed, and items are extracted and inserted into ERPNext.
    """
    try:
        content = await file.read()
        items = processor.process_file(content, file.filename)

        client = get_erp_client()
        results = []

        if client:
            for item in items:
                # Basic validation before sending
                if "item_code" in item:
                    res = client.create_item(item)
                    results.append(
                        {"item": item.get("item_code"), "result": res})
                else:
                    results.append(
                        {"item": "unknown", "result": "skipped: no item_code"})
        else:
            results = [
                {"message": "Processed but ERPNext client not configured", "data": items}]

        return {"filename": file.filename, "extracted_count": len(items), "results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
