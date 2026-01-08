import io
import os
import json
import pandas as pd
from pypdf import PdfReader
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class FileProcessor:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash') # Use flash for speed/cost
        else:
            print("Warning: GEMINI_API_KEY not found. Fallback to naive parsing.")
            self.model = None

    def process_file(self, file_content: bytes, filename: str) -> list:
        if filename.endswith('.pdf'):
            return self._process_pdf(file_content)
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            return self._process_excel(file_content)
        else:
            raise ValueError("Unsupported file type")

    def _process_pdf(self, content: bytes) -> list:
        text_content = ""
        
        # 1. Try extracting text directly
        try:
            reader = PdfReader(io.BytesIO(content))
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_content += text + "\n"
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")

        # 2. If text is sparse, use OCR on images
        if len(text_content.strip()) < 50:
            print("Text content low, attempting OCR...")
            try:
                images = convert_from_bytes(content)
                ocr_text = ""
                for img in images:
                    ocr_text += pytesseract.image_to_string(img) + "\n"
                text_content += "\n" + ocr_text
            except Exception as e:
                print(f"Error performing OCR: {e}")

        return self._parse_text_to_items(text_content)

    def _process_excel(self, content: bytes) -> list:
        try:
            df = pd.read_excel(io.BytesIO(content))
            # Basic validation: check if columns resemble item structure
            # For now, we convert rows to dicts
            # We filter out empty rows
            items = df.dropna(how='all').to_dict(orient='records')
            return self._normalize_items(items)
        except Exception as e:
            raise ValueError(f"Error processing Excel: {e}")

    def _parse_text_to_items(self, text: str) -> list:
        """
        Uses Gemini to parse unstructured text into structured Item data.
        """
        if not self.model:
             return self._naive_parse(text)

        prompt = f"""
        You are an intelligent data extraction assistant for an ERP system.
        Extract a list of Product Items from the following text.
        
        The Output must be a valid JSON list of objects.
        Each object should attempt to have these fields:
        - "item_code": A unique code if present, otherwise generate a sensible one based on name.
        - "item_name": The name of the product.
        - "description": Detailed description.
        - "item_group": The category of the item (guess if not explicit, default to 'All Item Groups').
        - "stock_uom": Unit of measure (e.g., Nos, Kg, Box). Default to 'Nos'.
        - "standard_rate": Price if available.
        
        If the text contains no items, return an empty list [].
        
        Text to process:
        \"\"\"
        {text[:10000]} 
        \"\"\"
        """ 
        # Truncate text to avoid token limits if extremely large, though flash handles ~1M tokens. 
        # 10k chars is safe for simple files.

        try:
            response = self.model.generate_content(prompt)
            # Cleanup Markdown code blocks if present
            raw_json = response.text.strip()
            if raw_json.startswith("```json"):
                raw_json = raw_json[7:-3]
            elif raw_json.startswith("```"):
                raw_json = raw_json[3:-3]
            
            items = json.loads(raw_json)
            if isinstance(items, list):
                return self._normalize_items(items)
            else:
                 print("Gemini returned non-list JSON.")
                 return self._naive_parse(text)

        except Exception as e:
            print(f"Gemini processing error: {e}")
            return self._naive_parse(text)

    def _naive_parse(self, text: str) -> list:
        """Fallback naive parser"""
        items = []
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 5:
                 items.append({
                    "description": line, 
                    "item_name": line[:100], 
                    "item_code": f"GEN-{hash(line) % 10000}"
                })
        return self._normalize_items(items)

    def _normalize_items(self, items: list) -> list:
        """
        Map columns to ERPNext Item fields.
        """
        normalized = []
        for item in items:
            new_item = {}
            for k, v in item.items():
                key = str(k).strip().lower().replace(" ", "_")
                new_item[key] = v
            
            if "item_code" not in new_item:
                 new_item["item_code"] = str(new_item.get("code", new_item.get("id", f"AUTO-{pd.Timestamp.now().timestamp()}")))
            
            if "item_name" not in new_item:
                new_item["item_name"] = str(new_item.get("name", new_item.get("description", "Unknown Item")))
            
            if "item_group" not in new_item:
                new_item["item_group"] = "All Item Groups" 
            
            if "stock_uom" not in new_item:
                new_item["stock_uom"] = "Nos" 
                
            normalized.append(new_item)
        return normalized
