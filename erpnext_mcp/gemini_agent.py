from google import genai
from google.genai import types
import json
import typing_extensions as typing
from config import GEMINI_API_KEY

class ProductItem(typing.TypedDict):
    item_code: str
    item_name: str
    description: str
    item_group: str
    stock_uom: str
    standard_rate: float
    is_stock_item: int

def extract_product_data(text_content):
    """
    Uses Gemini to extract a list of product items from the text content.
    Returns a list of dictionaries matching ERPNext Item schema.
    """
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    You are a data extraction assistant. Your task is to extract product information from the provided text.
    The text may come from an Excel sheet or a PDF (potentially OCR'd).
    
    Extract the following fields for each product found:
    - item_code (Unique identifier, if available, otherwise suggest a short unique code based on name)
    - item_name (Name of the product)
    - description (Detailed description)
    - item_group (Category of the item. e.g., 'Products', 'Services', 'Raw Material'. Default to 'All Item Groups' if unsure)
    - stock_uom (Unit of Measure, e.g., 'Nos', 'Kg', 'Ltr'. Default to 'Nos')
    - standard_rate (Price/Cost)
    - is_stock_item (1 for Yes, 0 for No. Default to 1)

    Input Text:
    {text_content}
    
    Return the data as a JSON list of objects.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", # Updated to a newer model standard with the new SDK usually
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=list[ProductItem]
            )
        )
        
        # In the new SDK, parsed response might be available directly if schema is provided, 
        # but often it returns an object that matches the schema.
        # However, purely checking text often works safest if we are just parsing internal JSON.
        # But if we use response_schema, the .parsed field should populate.
        
        if response.parsed:
             # creating a clean list of dicts from the parsed object
             return [item for item in response.parsed]
        
        text_resp = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text_resp)
        
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return []
