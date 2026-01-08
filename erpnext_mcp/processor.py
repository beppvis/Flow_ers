import pandas as pd
import pypdf
from pdf2image import convert_from_path
import pytesseract
import os

def process_excel(file_path):
    """
    Reads an Excel file and returns string representation of its content.
    """
    try:
        # Read all sheets
        xls = pd.ExcelFile(file_path)
        text_content = ""
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            text_content += f"Sheet: {sheet_name}\n"
            text_content += df.to_string() + "\n\n"
        return text_content
    except Exception as e:
        return f"Error processing Excel file: {e}"

def process_pdf(file_path):
    """
    Reads a PDF file. Extracts text directly. 
    If text is sparse (likely scanned), uses OCR on images.
    """
    try:
        text_content = ""
        
        # Try extracting text directly
        reader = pypdf.PdfReader(file_path)
        direct_text = ""
        for page in reader.pages:
            direct_text += page.extract_text() + "\n"
        
        text_content += "Direct Text Extracted:\n" + direct_text + "\n\n"

        # If direct text is very short/empty, assume it's an image/scanned PDF and use OCR
        # Heuristic: less than 50 characters per page on average might indicate scanned doc
        if len(direct_text.strip()) < 50 * len(reader.pages):
            print("Direct text extraction yielded little result. Attempting OCR...")
            images = convert_from_path(file_path)
            ocr_text = ""
            for i, image in enumerate(images):
                page_text = pytesseract.image_to_string(image)
                ocr_text += f"Page {i+1} OCR:\n{page_text}\n"
            
            text_content += "OCR Text Extracted:\n" + ocr_text
        
        return text_content
            
    except Exception as e:
        return f"Error processing PDF file: {e}"
