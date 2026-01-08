import os
from dotenv import load_dotenv

load_dotenv()

ERPNEXT_URL = os.getenv("ERPNEXT_URL")
ERPNEXT_API_KEY = os.getenv("ERPNEXT_API_KEY")
ERPNEXT_API_SECRET = os.getenv("ERPNEXT_API_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not ERPNEXT_URL:
    raise ValueError("ERPNEXT_URL is not set in environment variables")
if not ERPNEXT_API_KEY:
    raise ValueError("ERPNEXT_API_KEY is not set in environment variables")
if not ERPNEXT_API_SECRET:
    raise ValueError("ERPNEXT_API_SECRET is not set in environment variables")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in environment variables")
