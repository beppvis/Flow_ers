import os
import sys

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

def test_imports():
    print("Testing imports...")
    try:
        import fastapi
        import frappeclient
        import pandas
        import openpyxl
        import pdf2image
        import pytesseract
        import pypdf
        from google import genai
        print("Imports successful.")
    except ImportError as e:
        print(f"Import failed: {e}")
        sys.exit(1)

def test_processor_init():
    print("Testing processor init...")
    from processor import FileProcessor
    fp = FileProcessor()
    print("Processor initialized.")

if __name__ == "__main__":
    test_imports()
    test_processor_init()
