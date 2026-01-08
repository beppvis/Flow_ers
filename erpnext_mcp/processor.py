import io
import os
import json
import pandas as pd
from pypdf import PdfReader
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
from google import genai
from dotenv import load_dotenv

load_dotenv()


class FileProcessor:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            self.model_id = 'gemini-2.0-flash-exp'
        else:
            print("Warning: GEMINI_API_KEY not found. Fallback to naive parsing.")
            self.client = None

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
            # The excel files are likely invoices layout, not clean tables.
            # We convert the dataframe to a string representation (CSV) and let Gemini parse it.
            # distinct values might be sparse, so to_csv is a good representation.
            text_representation = df.to_csv(index=False)
            return self._parse_text_to_items(text_representation)
        except Exception as e:
            raise ValueError(f"Error processing Excel: {e}")

    def _parse_text_to_items(self, text: str) -> list:
        """
        Uses Gemini to parse unstructured text into structured Item data.
        """
        if not self.client:
            return self._naive_parse(text)

        prompt = f"""
        You are an intelligent data extraction assistant for an ERP system.

        Step 1: Analyze the text to determine if it is a relevant business document (Invoice, Quote, Receipt, Purchase Order, or Product List/Catalog).
        Step 2: If it is NOT relevant (e.g., a recipe, a poem, a legal contract, general news, or random text), return a JSON object indicating invalidity.
        Step 3: If it IS relevant, extract a list of Product Items.

        Output must be a valid JSON object with the following structure:
        {{
            "is_valid_document": boolean,
            "validation_reason": "string (Why is it valid or invalid?)",
            "items": [
                {{
                    "item_code": "Concise, uppercase, slug-like code (e.g. 'WLESS-MOUSE')",
                    "item_name": "Product Name",
                    "description": "Full description",
                    "item_group": "Inferred Category (e.g. Electronics, Packaging)",
                    "stock_uom": "Unit (Nos, Kg, Box)",
                    "standard_rate": 0.0
                }}
            ]
        }}

        Do NOT write markdown code blocks. Just return the raw JSON.

        Text to process:
        \"\"\"
        {text[:10000]}
        \"\"\"
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )

            # Cleanup if markdown blocks persist despite instructions
            raw_json = response.text.strip()
            if raw_json.startswith("```json"):
                raw_json = raw_json[7:-3]
            elif raw_json.startswith("```"):
                raw_json = raw_json[3:-3]

            result = json.loads(raw_json)

            # handle list or dict (legacy model might return list directly if prompt ignored)
            if isinstance(result, list):
                # Fallback implementation if model ignored structure
                return self._normalize_items(result)

            if not result.get("is_valid_document", True):
                reason = result.get(
                    "validation_reason", "Document does not appear to be a valid invoice or quote.")
                raise ValueError(f"Invalid Document: {reason}")

            items = result.get("items", [])
            return self._normalize_items(items)

        except ValueError as ve:
            # Re-raise validation errors
            raise ve
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
                new_item["item_code"] = str(new_item.get("code", new_item.get(
                    "id", f"AUTO-{pd.Timestamp.now().timestamp()}")))

            if "item_name" not in new_item:
                new_item["item_name"] = str(new_item.get(
                    "name", new_item.get("description", "Unknown Item")))

            if "item_group" not in new_item:
                new_item["item_group"] = "All Item Groups"

            if "stock_uom" not in new_item:
                new_item["stock_uom"] = "Nos"

            normalized.append(new_item)
        return normalized
