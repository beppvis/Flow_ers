import os
from processor import process_excel, process_pdf
from gemini_agent import extract_product_data
from erpnext_client import ERPNextClient


def core_process_file(file_path: str) -> str:
    """
    Core logic to process a file and create products in ERPNext.
    Returns a string report.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"

    # 1. Process File
    print(f"Processing file: {file_path}")
    ext = os.path.splitext(file_path)[1].lower()

    if ext in ['.xls', '.xlsx']:
        text_content = process_excel(file_path)
    elif ext == '.pdf':
        text_content = process_pdf(file_path)
    else:
        return f"Error: Unsupported file format {ext}. Please provide .xlsx, .xls, or .pdf"

    if text_content.startswith("Error"):
        return text_content

    # 2. Extract Data
    print("Extracting data with Gemini...")
    items_data = extract_product_data(text_content)

    if not items_data:
        return "No product data extraction could be performed or no data found."

    # 3. Create Items in ERPNext
    client = ERPNextClient()
    results = []

    print(f"Found {len(items_data)} items. Creating in ERPNext...")

    for item in items_data:
        try:
            # check if item exists
            existing_item = client.get_item(item['item_code'])
            if existing_item:
                results.append(f"Skipped: Item {
                               item['item_code']} already exists.")
            else:
                created_item = client.create_item(item)
                results.append(f"Success: Created item {
                               created_item['item_code']} ({created_item['item_name']})")
        except Exception as e:
            results.append(f"Failed: Item {item.get(
                'item_code', 'UNKNOWN')} - {str(e)}")

    return "\n".join(results)
